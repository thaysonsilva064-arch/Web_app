
import { auth, db, googleProvider, githubProvider } from '../firebase';
import { 
  signInWithPopup, 
  signOut, 
  onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { 
  doc, 
  getDoc, 
  setDoc, 
  updateDoc, 
  collection, 
  getDocs, 
  onSnapshot,
  query,
  where
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";
import { User, Config, BanInfo } from '../types';

export const firebaseService = {
  login: async (providerType: 'google' | 'github') => {
    const provider = providerType === 'google' ? googleProvider : githubProvider;
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      
      // Salva ou atualiza usuário no Firestore
      const userRef = doc(db, "users", user.uid);
      const userData: User = {
        id: user.uid,
        name: user.displayName || 'Usuário',
        email: user.email || '',
        provider: providerType,
        ip: 'Verificando...', // Em um app real usaríamos uma API de IP
        loginTime: new Date().toLocaleString()
      };
      await setDoc(userRef, userData, { merge: true });
      return userData;
    } catch (error: any) {
      if (error.code === 'auth/operation-not-allowed') {
        throw new Error("Provedor não habilitado no Firebase Console. Ative Google/GitHub em 'Authentication > Sign-in method'.");
      }
      throw error;
    }
  },

  logout: () => signOut(auth),

  getConfig: async (): Promise<Config> => {
    const configRef = doc(db, "settings", "app_config");
    const snap = await getDoc(configRef);
    if (snap.exists()) return snap.data() as Config;
    
    // Default se não existir
    const defaultConfig = { mainPassword: '11', adminPassword: '12' };
    await setDoc(configRef, defaultConfig);
    return defaultConfig;
  },

  updateConfig: async (newConfig: Config) => {
    const configRef = doc(db, "settings", "app_config");
    await updateDoc(configRef, { ...newConfig });
  },

  getAllUsers: async (): Promise<User[]> => {
    const querySnapshot = await getDocs(collection(db, "users"));
    return querySnapshot.docs.map(doc => doc.data() as User);
  },

  banUser: async (userId: string, reason: string) => {
    const banRef = doc(db, "bans", userId);
    await setDoc(banRef, { isBanned: true, reason, userId });
  },

  unbanUser: async (userId: string) => {
    const banRef = doc(db, "bans", userId);
    await setDoc(banRef, { isBanned: false });
  },

  subscribeToBan: (userId: string, callback: (ban: BanInfo | null) => void) => {
    return onSnapshot(doc(db, "bans", userId), (doc) => {
      if (doc.exists() && doc.data().isBanned) {
        callback(doc.data() as BanInfo);
      } else {
        callback(null);
      }
    });
  }
};
