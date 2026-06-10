#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

DEFAULT_REQUEST_FILE = Path('scripts/api-tests.json')
DEFAULT_RESPONSE_FILE = Path('scripts/api-response.json')
PLACEHOLDER_RE = re.compile(r"{{\s*([\w.-]+)\s*}}")


@dataclass
class RunSummary:
    total: int = 0
    executed: int = 0
    skipped: int = 0
    passed: int = 0
    failed: int = 0
    server_errors: int = 0


class JsonApiRunner:
    def __init__(self, request_file: Path, response_file: Path) -> None:
        self.request_file = request_file
        self.response_file = response_file
        self.config = self._load_json(self.request_file)
        self.base_url = str(self.config.get('base_url', 'http://localhost:8000')).rstrip('/')
        self.variables: dict[str, Any] = {
            **self.config.get('variables', {}),
            'baseUrl': self.base_url,
            'base_url': self.base_url,
            'now': self._now_iso(),
            'today': self._today(),
            'tomorrow': self._tomorrow(),
        }
        self.token: str = ''
        self.results: list[dict[str, Any]] = []
        self.summary = RunSummary(total=len(self.config.get('cases', [])))

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open('r', encoding='utf-8') as fh:
            return json.load(fh)

    @staticmethod
    def _write_json(path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
            fh.write('\n')

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

    @staticmethod
    def _today() -> str:
        return datetime.now(timezone.utc).date().isoformat()

    @staticmethod
    def _tomorrow() -> str:
        from datetime import timedelta
        return (datetime.now(timezone.utc).date() + timedelta(days=1)).isoformat()

    def _template_value(self, value: Any) -> Any:
        if isinstance(value, str):
            exact = PLACEHOLDER_RE.fullmatch(value.strip())
            if exact:
                key = exact.group(1)
                if key in self.variables:
                    return self.variables[key]
                if key == 'token':
                    return self.token

            def replace(match: re.Match[str]) -> str:
                key = match.group(1)
                if key in self.variables:
                    return str(self.variables[key])
                if key == 'token':
                    return self.token
                return match.group(0)

            return PLACEHOLDER_RE.sub(replace, value)
        if isinstance(value, list):
            return [self._template_value(item) for item in value]
        if isinstance(value, dict):
            return {key: self._template_value(item) for key, item in value.items()}
        return value

    def _response_body(self, response: httpx.Response) -> Any:
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type:
            try:
                return response.json()
            except Exception:
                return response.text
        try:
            return response.json()
        except Exception:
            return response.text

    @staticmethod
    def _normalize_expected(expected: Any) -> list[int]:
        if expected is None:
            return []
        if isinstance(expected, int):
            return [expected]
        if isinstance(expected, list):
            return [int(item) for item in expected]
        return [int(expected)]

    def _print_case(self, case: dict[str, Any], request: dict[str, Any], response: httpx.Response | None, skipped: bool = False) -> None:
        print(f"\n=== {case['name']} ===")
        print(f"{request['method']} {self.base_url}{request['path']}")
        if request.get('query'):
            print('Query:')
            print(json.dumps(request['query'], indent=2, ensure_ascii=False))
        print('Request body:')
        print(json.dumps(request.get('body'), indent=2, ensure_ascii=False) if request.get('body') is not None else '<none>')
        if skipped:
            print('Response: <skipped>')
            return
        assert response is not None
        print(f'Response status: {response.status_code}')
        print('Response body:')
        print(json.dumps(self._response_body(response), indent=2, ensure_ascii=False) if self._response_body(response) is not None else '<none>')

    async def run(self) -> None:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            for case in self.config.get('cases', []):
                method = str(case.get('method', 'GET')).upper()
                enabled = bool(case.get('enabled', True))
                path = self._template_value(case.get('path', ''))
                query = self._template_value(case.get('query', {})) or None
                body = self._template_value(case.get('body'))
                headers = self._template_value(case.get('headers', {})) or {}
                auth = bool(case.get('auth', True))
                expected_status = self._normalize_expected(case.get('expect_status'))

                request_record = {
                    'method': method,
                    'path': path,
                    'query': query,
                    'body': body,
                    'headers': headers,
                    'auth': auth,
                    'enabled': enabled,
                }

                if not enabled:
                    self.summary.skipped += 1
                    self.results.append({
                        'name': case.get('name', path),
                        'request': request_record,
                        'response': None,
                        'expected_status': expected_status,
                        'passed': None,
                        'skipped': True,
                    })
                    self._print_case(case, request_record, None, skipped=True)
                    continue

                request_headers: dict[str, str] = dict(headers) if isinstance(headers, dict) else {}
                if body is not None:
                    request_headers.setdefault('Content-Type', 'application/json')
                if auth and path != '/api/v1/auth/login':
                    if not self.token:
                        raise RuntimeError(f"Case '{case.get('name')}' requires auth but no token has been captured yet. Put Login first.")
                    request_headers['Authorization'] = f'Bearer {self.token}'

                response = await client.request(method, path, params=query, json=body if body is not None else None, headers=request_headers)
                response_body = self._response_body(response)
                if path == '/api/v1/auth/login' and response.is_success and isinstance(response_body, dict) and response_body.get('access_token'):
                    self.token = str(response_body['access_token'])
                    self.variables['token'] = self.token

                passed = True if not expected_status else response.status_code in expected_status
                if response.status_code >= 500:
                    self.summary.server_errors += 1
                self.summary.executed += 1
                if passed:
                    self.summary.passed += 1
                else:
                    self.summary.failed += 1

                self.results.append({
                    'name': case.get('name', path),
                    'request': request_record,
                    'response': {
                        'status': response.status_code,
                        'headers': dict(response.headers),
                        'body': response_body,
                    },
                    'expected_status': expected_status,
                    'passed': passed,
                    'skipped': False,
                })
                self._print_case(case, request_record, response)

        output = {
            'generated_at': self._now_iso(),
            'base_url': self.base_url,
            'request_file': str(self.request_file),
            'summary': {
                'total': self.summary.total,
                'executed': self.summary.executed,
                'skipped': self.summary.skipped,
                'passed': self.summary.passed,
                'failed': self.summary.failed,
                'server_errors': self.summary.server_errors,
            },
            'results': self.results,
        }
        self._write_json(self.response_file, output)
        print(f"\nWrote response JSON to: {self.response_file}")
        print(json.dumps(output['summary'], indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run JSON-defined API tests and export JSON responses.')
    parser.add_argument('--request-file', default=str(DEFAULT_REQUEST_FILE), help='Path to request JSON file')
    parser.add_argument('--response-file', default=str(DEFAULT_RESPONSE_FILE), help='Path to output response JSON file')
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    runner = JsonApiRunner(Path(args.request_file), Path(args.response_file))
    await runner.run()


if __name__ == '__main__':
    asyncio.run(main())
