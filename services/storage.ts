
import { User, Config, BanInfo } from '../types';

const STORAGE_KEYS = {
  USERS: 'app_users',
  CONFIG: 'app_config',
  BANNED: 'app_banned',
  SESSION: 'app_session'
};

export const storage = {
  getUsers: (): User[] => JSON.parse(localStorage.getItem(STORAGE_KEYS.USERS) || '[]'),
  saveUser: (user: User) => {
    const users = storage.getUsers();
    if (!users.find(u => u.id === user.id)) {
      localStorage.setItem(STORAGE_KEYS.USERS, JSON.stringify([...users, user]));
    }
  },
  getConfig: (): Config => JSON.parse(localStorage.getItem(STORAGE_KEYS.CONFIG) || JSON.stringify({
    mainPassword: '11',
    adminPassword: '12'
  })),
  saveConfig: (config: Config) => localStorage.setItem(STORAGE_KEYS.CONFIG, JSON.stringify(config)),
  getBanned: (): BanInfo[] => JSON.parse(localStorage.getItem(STORAGE_KEYS.BANNED) || '[]'),
  banUser: (userId: string, reason: string) => {
    const banned = storage.getBanned();
    if (!banned.find(b => b.userId === userId)) {
      localStorage.setItem(STORAGE_KEYS.BANNED, JSON.stringify([...banned, { isBanned: true, reason, userId }]));
    }
  },
  unbanUser: (userId: string) => {
    const banned = storage.getBanned().filter(b => b.userId !== userId);
    localStorage.setItem(STORAGE_KEYS.BANNED, JSON.stringify(banned));
  },
  getSession: (): User | null => JSON.parse(localStorage.getItem(STORAGE_KEYS.SESSION) || 'null'),
  setSession: (user: User | null) => localStorage.setItem(STORAGE_KEYS.SESSION, JSON.stringify(user)),
  clearAll: () => localStorage.clear()
};
