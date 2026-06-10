import { Component } from '@angular/core';

import { SyncResourcePanelComponent } from '../../shared/components/sync-resource-panel.component';

@Component({
	selector: 'app-menu-sync-page',
	standalone: true,
	imports: [SyncResourcePanelComponent],
	template: `
		<app-sync-resource-panel
			resource="menu"
			title="Menu sync"
			description="Sync the backend menu seed into persisted admin configuration records."
			pageTestId="menu-sync-page"
			buttonTestId="sync-menu-button"
		></app-sync-resource-panel>
	`,
	styles: []
})
export class MenuSyncPageComponent {}
