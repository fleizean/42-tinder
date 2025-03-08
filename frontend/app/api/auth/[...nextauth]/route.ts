import NextAuth from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        usernameOrEmail: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
        loginType: { label: "Login Type", type: "text" },
        accessToken: { label: "Access Token", type: "text" },
        refreshToken: { label: "Refresh Token", type: "text" }
      },
      async authorize(credentials) {
        try {
          // Google Login
          if (credentials?.loginType === 'google') {
            const tokenData = JSON.parse(atob(credentials.accessToken.split('.')[1]));
            const expirationTime = tokenData.exp * 1000
            return {
              id: '1',
              accessToken: credentials.accessToken,
              refreshToken: credentials.refreshToken,
              expiration: new Date(expirationTime).toISOString()
            };
          }

          // Regular Login
          const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_API_URL}/api/Auth/login`, {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              usernameOrEmail: credentials?.usernameOrEmail,
              password: credentials?.password,
            })
          });

          const data = await res.json();

          if (data.status) {
            const tokenData = JSON.parse(atob(data.data.accessToken.split('.')[1]));
            const expirationTime = tokenData.exp * 1000;

            return {
              id: credentials?.usernameOrEmail || '1',
              accessToken: data.data.accessToken,
              refreshToken: data.data.refreshToken,
              expiration: new Date(expirationTime).toISOString()
            };
          }
          return null;
        } catch (error) {
          console.error("Auth error:", error);
          return null;
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
        token.expiration = user.expiration;
      }
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.accessToken = token.accessToken;
        session.user.refreshToken = token.refreshToken;
        session.user.expiration = token.expiration;
      }
      if (token.expiration && new Date(token.expiration) < new Date()) {
        return null; // Force re-authentication
      }
      return session;
    }
  },
  pages: {
    signIn: '/signin',
    error: '/auth/error'
  },
  debug: process.env.NODE_ENV === 'development'
});

export { handler as GET, handler as POST };