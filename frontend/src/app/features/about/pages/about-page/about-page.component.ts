import { ChangeDetectionStrategy, Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslatePipe } from '../../../../core/i18n/translate.pipe';
import { SeoService } from '../../../../core/seo/seo.service';

interface AboutExperienceItem {
  readonly titleKey: string;
  readonly company: string;
  readonly descriptionKey: string;
  readonly periodStart: string;
  readonly periodEnd: string | null;
  readonly periodEndKey: string | null;
  readonly skills: readonly string[];
}

@Component({
  selector: 'app-about-page',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterLink, TranslatePipe],
  templateUrl: './about-page.component.html',
})
export class AboutPageComponent implements OnInit {
  readonly experienceItems: readonly AboutExperienceItem[] = [
    {
      titleKey: 'about.job.seniorBackendDeveloper',
      company: 'START',
      descriptionKey: 'about.job.startStreaming',
      periodStart: '05/2026',
      periodEnd: null,
      periodEndKey: 'about.job.present',
      skills: ['Python', 'Backend', 'Microservices', 'High-load', 'CI/CD'],
    },
    {
      titleKey: 'about.job.seniorBackendPythonTechLead',
      company: 'Compel',
      descriptionKey: 'about.job.compelB2bAi',
      periodStart: '08/2024',
      periodEnd: '04/2026',
      periodEndKey: null,
      skills: [
        'Python',
        'FastAPI',
        'SQLAlchemy',
        'PostgreSQL',
        'MongoDB',
        'Kafka',
        'FastStream',
        'MinIO',
        'Qdrant',
        'LangChain',
        'RAG',
        'Kubernetes',
        'Terraform',
        'OpenTelemetry',
        'Locust',
      ],
    },
    {
      titleKey: 'about.job.leadBackendHeadOfPython',
      company: 'Fortech',
      descriptionKey: 'about.job.fortechFitnessPets',
      periodStart: '06/2022',
      periodEnd: '08/2024',
      periodEndKey: null,
      skills: [
        'Python',
        'Django',
        'DRF',
        'FastAPI',
        'SQLAlchemy',
        'PostgreSQL',
        'PostGIS',
        'GeoAlchemy2',
        'Redis',
        'RabbitMQ',
        'Celery',
        'Django-Channels',
        'MinIO',
        'Kubernetes',
        'Helm',
        'gRPC',
      ],
    },
    {
      titleKey: 'about.job.seniorBackendDeveloper',
      company: 'Fortech',
      descriptionKey: 'about.job.fortechHrRecruitment',
      periodStart: '01/2021',
      periodEnd: '06/2022',
      periodEndKey: null,
      skills: [
        'Python',
        'FastAPI',
        'Pydantic',
        'SQLAlchemy',
        'PostgreSQL',
        'Redis',
        'Kafka',
        'MinIO',
        'Portainer',
        'PyTest',
      ],
    },
    {
      titleKey: 'about.job.backendDeveloper',
      company: 'Fortech',
      descriptionKey: 'about.job.fortechEarlyProjects',
      periodStart: '02/2020',
      periodEnd: '01/2021',
      periodEndKey: null,
      skills: [
        'Python',
        'Django',
        'DRF',
        'Sanic',
        'aiohttp',
        'PostgreSQL',
        'SQLite',
        'Celery',
        'RabbitMQ',
        'Redis',
        'OpenCV',
        'PyQt6',
        'PyTest',
      ],
    },
  ];

  private readonly seoService = inject(SeoService);

  ngOnInit(): void {
    this.seoService.setTranslatedMeta({
      titleKey: 'about.seo.title',
      descriptionKey: 'about.seo.description',
      canonicalPath: '/about-me',
    });
  }
}
