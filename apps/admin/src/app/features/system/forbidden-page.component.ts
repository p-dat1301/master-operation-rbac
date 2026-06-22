import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzResultModule } from 'ng-zorro-antd/result';

@Component({
	selector: 'app-forbidden-page',
	standalone: true,
	imports: [RouterModule, NzButtonModule, NzResultModule],
	template: `
		<nz-result
			data-testid="forbidden-page"
			nzStatus="403"
			nzTitle="Không đủ quyền"
			nzSubTitle="Tài khoản hiện tại không có quyền truy cập màn hình này."
		>
			<div nz-result-extra>
				<a nz-button nzType="primary" routerLink="/" aria-label="Quay về trang tổng quan">Về tổng quan</a>
			</div>
		</nz-result>
	`
})
export class ForbiddenPageComponent {}
