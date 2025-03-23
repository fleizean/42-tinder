export type LoginResponse = {
  status: boolean;
  message: string;
  data: {
    accessToken: string;
    refreshToken: string;
    expiration: string;
  }
}