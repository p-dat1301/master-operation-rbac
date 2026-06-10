import { ApplicationConfig, importProvidersFrom, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideNzIcons } from 'ng-zorro-antd/icon';
import { NZ_CONFIG, NzConfig } from 'ng-zorro-antd/core/config';
import { NzModalModule } from 'ng-zorro-antd/modal';
import { AppstoreOutline, DashboardOutline, MenuFoldOutline, MenuUnfoldOutline, TranslationOutline } from '@ant-design/icons-angular/icons';

import { authInterceptor } from './core/interceptors/auth.interceptor';
import { API_BASE_URL } from './core/tokens/api-base-url.token';
import { routes } from './app.routes';

const ngZorroConfig: NzConfig = {
  // place global NG ZORRO configs here (icons, z-index, etc.)
};

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),
    provideNzIcons([MenuFoldOutline, MenuUnfoldOutline, DashboardOutline, AppstoreOutline, TranslationOutline]),
    importProvidersFrom(NzModalModule),
    { provide: API_BASE_URL, useValue: 'http://127.0.0.1:8010/api/v1' },
    { provide: NZ_CONFIG, useValue: ngZorroConfig }
  ]
};
