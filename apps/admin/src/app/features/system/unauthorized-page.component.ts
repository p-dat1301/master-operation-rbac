import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzResultModule } from 'ng-zorro-antd/result';

@Component({
	selector: 'app-unauthorized-page',
	standalone: true,
	imports: [RouterModule, NzButtonModule, NzResultModule],
	template: `
		<nz-result
			data-testid="unauthorized-page"
			nzStatus="403"
			nzTitle="Cần đăng nhập"
			nzSubTitle="Vui lòng đăng nhập để tiếp tục vào khu vực quản trị."
		>
			<div nz-result-extra>
				<a nz-button nzType="primary" routerLink="/login" aria-label="Đi tới trang đăng nhập">Đăng nhập</a>
			</div>
		</nz-result>
	`
})
export class UnauthorizedPageComponent {}
