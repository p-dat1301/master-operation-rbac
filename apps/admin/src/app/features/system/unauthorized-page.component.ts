import { Component } from '@angular/core';
import { NzResultModule } from 'ng-zorro-antd/result';

@Component({
	selector: 'app-unauthorized-page',
	standalone: true,
	imports: [NzResultModule],
	template: `
		<nz-result
			nzStatus="warning"
			nzTitle="Unauthorized"
			nzSubTitle="Please sign in to continue to the admin workspace."
		></nz-result>
	`
})
export class UnauthorizedPageComponent {}
