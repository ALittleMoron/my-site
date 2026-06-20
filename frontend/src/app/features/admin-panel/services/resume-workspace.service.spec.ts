import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ApiClient } from '../../../core/http/api-client.service';
import { ResumePayload } from '../models/resume-workspace.model';
import { ResumeWorkspaceService } from './resume-workspace.service';

describe('ResumeWorkspaceService', () => {
  let service: ResumeWorkspaceService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        ResumeWorkspaceService,
        ApiClient,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(ResumeWorkspaceService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('loads admin resumes with explicit pagination', () => {
    let firstTitle = '';

    service.listResumes({ page: 2, pageSize: 20 }).subscribe((list) => {
      firstTitle = list.resumes[0].title;
    });

    const listReq = httpMock.expectOne((request) => request.url.endsWith('/api/admin/resumes'));
    expect(listReq.request.method).toBe('GET');
    expect(listReq.request.params.get('page')).toBe('2');
    expect(listReq.request.params.get('pageSize')).toBe('20');
    listReq.flush({
      totalCount: 1,
      totalPages: 1,
      resumes: [resumeDto()],
    });

    expect(firstTitle).toBe('Backend resume');
  });

  it('loads resume detail through the admin endpoint', () => {
    let fullName = '';

    service.getResume(7).subscribe((resume) => {
      fullName = resume.content.profile.fullName ?? '';
    });

    const detailReq = httpMock.expectOne((request) => request.url.endsWith('/api/admin/resumes/7'));
    expect(detailReq.request.method).toBe('GET');
    detailReq.flush(resumeDto());

    expect(fullName).toBe('Candidate Name');
  });

  it('creates, updates, and deletes resumes through admin endpoints', () => {
    const payload = resumePayload();

    service.createResume(payload).subscribe((resume) => {
      expect(resume.id).toBe(7);
    });
    const createReq = httpMock.expectOne((request) => request.url.endsWith('/api/admin/resumes'));
    expect(createReq.request.method).toBe('POST');
    expect(createReq.request.body).toEqual(payload);
    createReq.flush(resumeDto());

    service.updateResume(7, payload).subscribe((resume) => {
      expect(resume.title).toBe('Backend resume');
    });
    const updateReq = httpMock.expectOne((request) => request.url.endsWith('/api/admin/resumes/7'));
    expect(updateReq.request.method).toBe('PUT');
    expect(updateReq.request.body).toEqual(payload);
    updateReq.flush(resumeDto());

    service.deleteResume(7).subscribe();
    const deleteReq = httpMock.expectOne((request) => request.url.endsWith('/api/admin/resumes/7'));
    expect(deleteReq.request.method).toBe('DELETE');
    deleteReq.flush(null);
  });

  it('maps nested resume content without sharing mutable DTO arrays', () => {
    let payloadItems: readonly string[] = [];
    let payloadProjectTechnologies: readonly string[] = [];
    const dto = resumeDto();

    service.getResume(7).subscribe((resume) => {
      payloadItems = resume.content.skills[0].items;
      payloadProjectTechnologies = resume.content.experience[0].projects[0].technologies;
      resume.content.skills[0].items.push('TypeScript');
      resume.content.experience[0].projects[0].technologies.push('Angular');
    });

    const detailReq = httpMock.expectOne((request) => request.url.endsWith('/api/admin/resumes/7'));
    detailReq.flush(dto);

    expect(payloadItems).toEqual(['Python', 'PostgreSQL', 'TypeScript']);
    expect(payloadProjectTechnologies).toEqual(['Litestar', 'Angular']);
    expect(dto.content.skills[0].items).toEqual(['Python', 'PostgreSQL']);
    expect(dto.content.experience[0].projects[0].technologies).toEqual(['Litestar']);
  });
});

function resumePayload(): ResumePayload {
  return {
    title: 'Backend resume',
    content: resumeContent(),
  };
}

function resumeDto(): {
  id: number;
  title: string;
  content: ReturnType<typeof resumeContent>;
  createdAt: string;
  updatedAt: string;
} {
  return {
    id: 7,
    title: 'Backend resume',
    content: resumeContent(),
    createdAt: '2026-01-01T03:04:05+00:00',
    updatedAt: '2026-01-02T03:04:05+00:00',
  };
}

function resumeContent(): ResumePayload['content'] {
  return {
    profile: {
      fullName: 'Candidate Name',
      roleRu: 'Инженер',
      roleEn: 'Engineer',
      locationRu: null,
      locationEn: null,
      email: null,
      phone: null,
      websiteUrl: null,
      linkedinUrl: null,
      githubUrl: null,
      telegram: null,
    },
    summary: {
      textRu: 'Короткое описание опыта.',
      textEn: 'Short experience summary.',
    },
    skills: [
      {
        categoryRu: 'Backend',
        categoryEn: 'Backend',
        items: ['Python', 'PostgreSQL'],
      },
    ],
    experience: [
      {
        companyRu: 'Компания',
        companyEn: 'Company',
        positionRu: 'Инженер',
        positionEn: 'Engineer',
        locationRu: null,
        locationEn: null,
        startDate: '2020-01-01',
        endDate: null,
        isCurrent: true,
        summaryRu: 'Строил платформу.',
        summaryEn: 'Built a platform.',
        highlightsRu: ['Сократил latency'],
        highlightsEn: ['Reduced latency'],
        technologies: ['Python'],
        projects: [
          {
            nameRu: 'Портфолио',
            nameEn: 'Portfolio',
            roleRu: 'Автор',
            roleEn: 'Creator',
            descriptionRu: 'Сайт и база знаний',
            descriptionEn: 'Site and knowledge base',
            highlightsRu: ['Гибридный SSR/CSR'],
            highlightsEn: ['Hybrid SSR/CSR'],
            technologies: ['Litestar'],
            url: 'https://example.com',
          },
        ],
      },
    ],
    education: [],
    languages: [],
    certifications: [],
    additionalSections: [],
  };
}
