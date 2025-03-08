import NextAuth, { DefaultUser } from "next-auth"

declare module "next-auth" {
  interface User extends DefaultUser {
    id: string
    accessToken: string
    //refreshToken: string
    expiration: string
  }

  interface Session {
    user: User & {
      id: string
      name?: string
      email?: string
      accessToken: string
      //refreshToken: string
      expiration: string
    }
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    accessToken: string
    //refreshToken: string
    expiration: string
  }
}