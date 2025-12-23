
export enum View {
  LOGIN = 'LOGIN',
  MAIN_PANEL = 'MAIN_PANEL',
  ADMIN_PANEL = 'ADMIN_PANEL',
  BANNED = 'BANNED'
}

export interface User {
  id: string;
  name: string;
  email: string;
  provider: 'google' | 'github';
  ip: string;
  loginTime: string;
}

export interface BanInfo {
  isBanned: boolean;
  reason: string;
  userId: string;
}

export interface Config {
  mainPassword: string;
  adminPassword: string;
}
