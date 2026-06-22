import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzResultModule } from 'ng-zorro-antd/result';

@Component({
	selector: 'app-not-found-page',
	standalone: true,
	imports: [RouterModule, NzButtonModule, NzResultModule],
	template: `
		<nz-result
			data-testid="not-found-page"
			nzStatus="404"
			nzTitle="Không tìm thấy trang"
			nzSubTitle="Trang quản trị bạn yêu cầu không tồn tại."
		>
			<div nz-result-extra>
				<a nz-button nzType="primary" routerLink="/" aria-label="Quay về trang tổng quan">Về tổng quan</a>
			</div>
		</nz-result>
	`
})
export class NotFoundPageComponent {}
