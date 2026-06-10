import { Component } from '@angular/core';
import { NzResultModule } from 'ng-zorro-antd/result';

@Component({
	selector: 'app-forbidden-page',
	standalone: true,
	imports: [NzResultModule],
	template: `
		<nz-result
			data-testid="forbidden-page"
			nzStatus="403"
			nzTitle="Forbidden"
			nzSubTitle="You do not have permission to access this admin route."
		></nz-result>
	`
})
export class ForbiddenPageComponent {}
