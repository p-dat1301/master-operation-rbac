import { Component } from '@angular/core';
import { NzButtonModule } from 'ng-zorro-antd/button';

@Component({
  selector: 'app-home-page',
  standalone: true,
  template: `
    <section class="home-page" data-testid="admin-home-page">
      <div class="card">
        <p class="label">Workspace ready</p>
        <h2>Starter shell is live</h2>
        <p>
          This placeholder page keeps the admin workspace standalone-first and
          gives future feature routes a stable landing area.
        </p>

        <div class="mt-4 flex gap-3">
          <button nz-button nzType="primary" class="px-4 py-2 rounded text-white bg-sky-600">NG ZORRO Primary</button>
          <button class="px-4 py-2 rounded bg-gray-200 text-gray-800">Tailwind Button</button>
        </div>
      </div>
    </section>
  `,
  imports: [NzButtonModule],
  styles: [
    `
      :host {
        display: block;
      }

      .home-page {
        min-height: 14rem;
        display: grid;
        place-items: center;
      }

      .card {
        width: min(100%, 42rem);
        padding: 1.5rem;
        border-radius: 1.25rem;
        border: 1px solid rgba(148, 163, 184, 0.12);
        background: rgba(15, 23, 42, 0.65);
      }

      .label {
        margin: 0 0 0.5rem;
        font-size: 0.8rem;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #8ec5ff;
      }

      h2 {
        margin: 0;
        font-size: 1.5rem;
      }

      p {
        margin: 0.75rem 0 0;
        line-height: 1.65;
        color: rgba(226, 232, 240, 0.84);
      }
    `
  ]
})
export class HomePageComponent {}
