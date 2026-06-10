import { Component } from '@angular/core';

import { SyncResourcePanelComponent } from '../../shared/components/sync-resource-panel.component';

@Component({
	selector: 'app-i18n-sync-page',
	standalone: true,
	imports: [SyncResourcePanelComponent],
	template: `
		<app-sync-resource-panel
			resource="i18n"
			title="i18n sync"
			description="Sync locale seed files into translation records for the admin workspace."
			pageTestId="i18n-sync-page"
			buttonTestId="sync-i18n-button"
		></app-sync-resource-panel>
	`,
	styles: []
})
export class I18nSyncPageComponent {}
