export type ManagedAccountRole = 'owner' | 'admin' | 'moderator';
export type EditableManagedAccountRole = 'admin' | 'moderator';

export interface ManagedAccountDto {
  username: string;
  role: ManagedAccountRole;
  isActive: boolean;
}

export interface ManagedAccountsDto {
  totalCount: number;
  totalPages: number;
  accounts: ManagedAccountDto[];
}

export interface ManagedAccount {
  username: string;
  role: ManagedAccountRole;
  isActive: boolean;
}

export interface ManagedAccounts {
  totalCount: number;
  totalPages: number;
  accounts: ManagedAccount[];
}

export interface ManagedAccountListParams {
  page: number;
  pageSize: number;
}

export interface ManagedAccountCreatePayload {
  username: string;
  role: EditableManagedAccountRole;
  password: string;
  isActive: boolean;
}

export interface ManagedAccountRoleUpdatePayload {
  role: EditableManagedAccountRole;
}

export interface ManagedAccountPasswordUpdatePayload {
  password: string;
}

export function mapManagedAccountDto(dto: ManagedAccountDto): ManagedAccount {
  return {
    username: dto.username,
    role: dto.role,
    isActive: dto.isActive,
  };
}

export function mapManagedAccountsDto(dto: ManagedAccountsDto): ManagedAccounts {
  return {
    totalCount: dto.totalCount,
    totalPages: dto.totalPages,
    accounts: dto.accounts.map(mapManagedAccountDto),
  };
}
