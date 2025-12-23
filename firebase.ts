
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, GithubAuthProvider } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js";

// SUBSTITUA OS VALORES ABAIXO PELOS DO SEU FIREBASE CONSOLE
const firebaseConfig = {
  apiKey: "AIzaSyD93uDjIwxIMMi86YwEAPp-rEjgzblALhc",
  authDomain: "web-console-896dc.firebaseapp.com",
  projectId: "web-console-896dc",
  storageBucket: "web-console-896dc.firebasestorage.app",
  messagingSenderId: "654403534426",
  appId: "1:654403534426:web:1cdf3eb69b372037a46263"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();
export const githubProvider = new GithubAuthProvider();
