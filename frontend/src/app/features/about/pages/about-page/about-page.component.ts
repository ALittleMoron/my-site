import {
  ChangeDetectionStrategy,
  Component,
  DestroyRef,
  OnInit,
  computed,
  inject,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { finalize } from 'rxjs';
import { ApiError } from '../../../../core/models/api-error.model';
import { SeoService } from '../../../../core/seo/seo.service';
import { ContactService } from '../../services/contact.service';

@Component({
  selector: 'app-about-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './about-page.component.html',
})
export class AboutPageComponent implements OnInit {
  private readonly contactService = inject(ContactService);
  private readonly seoService = inject(SeoService);
  private readonly destroyRef = inject(DestroyRef);

  readonly form = new FormGroup({
    name: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.maxLength(255)],
    }),
    email: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.email, Validators.maxLength(255)],
    }),
    telegram: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.minLength(2), Validators.maxLength(256)],
    }),
    message: new FormControl<string>('', {
      nonNullable: true,
      validators: [Validators.required, Validators.maxLength(10000)],
    }),
  });

  readonly submitting = signal(false);
  readonly submitted = signal(false);
  readonly submitError = signal<ApiError | null>(null);
  readonly hasNestedErrors = computed(() => !!this.submitError()?.nested_errors?.length);

  ngOnInit(): void {
    this.seoService.setMeta({
      title: 'Обо мне',
      description: 'Личный сайт Дмитрия Лунева: портфолио, матрица компетенций и контактная форма.',
    });
  }

  submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();
    const request = {
      name: raw.name.trim() || null,
      email: raw.email.trim() || null,
      telegram: raw.telegram.trim() || null,
      message: raw.message,
    };

    this.submitting.set(true);
    this.submitError.set(null);

    this.contactService
      .createContactRequest(request)
      .pipe(
        takeUntilDestroyed(this.destroyRef),
        finalize(() => this.submitting.set(false)),
      )
      .subscribe({
        next: () => {
          this.submitted.set(true);
          this.form.reset();
        },
        error: (err: ApiError) => {
          this.submitError.set(err);
        },
      });
  }
}
