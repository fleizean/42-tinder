export type LoginResponse = {
  status: boolean;
  message: string;
  data: {
    accessToken: string;
    expiration: string;
    //refreshToken: string;
  }
}