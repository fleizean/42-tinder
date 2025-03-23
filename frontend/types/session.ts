import NextAuth from "next-auth"
import { User } from "next-auth"

declare module "next-auth" {
  interface Session {
    user: User & {
      id: string
      name?: string
      email?: string
      accessToken: string
      refreshToken: string
      expiration: string
    }
  }
}