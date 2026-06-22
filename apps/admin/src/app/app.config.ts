import { ApplicationConfig, importProvidersFrom, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideNzIcons } from 'ng-zorro-antd/icon';
import { NZ_CONFIG, NzConfig } from 'ng-zorro-antd/core/config';
import { NZ_I18N, vi_VN as nzViVN } from 'ng-zorro-antd/i18n';
import angularViVN from '@angular/common/locales/vi';
import { registerLocaleData } from '@angular/common';
import { NzModalModule } from 'ng-zorro-antd/modal';
import {
  AppstoreOutline, BellOutline, CalendarOutline, CheckCircleOutline, CheckSquareOutline,
  CloseCircleOutline, CloseOutline, CheckOutline, DatabaseOutline,
  DashboardOutline, DeleteOutline, EyeOutline, FileSearchOutline,
  KeyOutline, LockOutline, MenuFoldOutline, MenuUnfoldOutline,
  MessageOutline, PlayCircleOutline, PlusOutline, ReloadOutline, SafetyCertificateOutline,
  StopOutline, SyncOutline, TeamOutline, TranslationOutline
} from '@ant-design/icons-angular/icons';

import { authInterceptor } from './core/interceptors/auth.interceptor';
import { API_BASE_URL } from './core/tokens/api-base-url.token';
import { routes } from './app.routes';

registerLocaleData(angularViVN);

const ngZorroConfig: NzConfig = {};

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),
    provideNzIcons([
      MenuFoldOutline, MenuUnfoldOutline, DashboardOutline, AppstoreOutline, TranslationOutline,
      BellOutline, TeamOutline, SafetyCertificateOutline, KeyOutline,
      CheckSquareOutline, CalendarOutline, FileSearchOutline, DatabaseOutline,
      PlusOutline, DeleteOutline, ReloadOutline, SyncOutline,
      MessageOutline, PlayCircleOutline, CheckCircleOutline, CloseCircleOutline, CheckOutline, CloseOutline,
      StopOutline, LockOutline, EyeOutline
    ]),
    importProvidersFrom(NzModalModule),
    { provide: API_BASE_URL, useValue: 'http://127.0.0.1:8010' },
    { provide: NZ_CONFIG, useValue: ngZorroConfig },
    { provide: NZ_I18N, useValue: nzViVN }
  ]
};
