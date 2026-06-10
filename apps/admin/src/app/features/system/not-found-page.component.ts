import { Component } from '@angular/core';
import { NzResultModule } from 'ng-zorro-antd/result';

@Component({
	selector: 'app-not-found-page',
	standalone: true,
	imports: [NzResultModule],
	template: `
		<nz-result
			nzStatus="404"
			nzTitle="Page not found"
			nzSubTitle="The requested admin route does not exist."
		></nz-result>
	`
})
export class NotFoundPageComponent {}
