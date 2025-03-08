import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  async function middleware(req) {
    const authPages = ["/signin", "/signup", "/forgot-password"];
    const isAuthPage = authPages.includes(req.nextUrl.pathname);
    const token = req.nextauth?.token;


    if (req.nextUrl.pathname.startsWith('/profile')) {
      const segments = req.nextUrl.pathname.split('/');
      // Check if there's a username after /profile/
      if (segments.length < 3 || !segments[2]) {
        if (token)
          return NextResponse.redirect(new URL("/dashboard", req.url));
        else
          return NextResponse.redirect(new URL("/signin", req.url));
      }
    }
    
    if ((token?.expiration && Date.now() >= new Date(token.expiration).getTime()) || (!token && !isAuthPage && req.nextUrl.pathname !== "/")) {
      const response = NextResponse.redirect(new URL("/signin", req.url));

      // Çerezleri temizle
      response.cookies.delete("next-auth.session-token");
      response.cookies.delete("next-auth.callback-url");
      response.cookies.delete("accessToken");
      //response.cookies.delete("refreshToken");

      return response;
    }

    // Kullanıcı giriş yapmışsa ve auth sayfasına gidiyorsa, yönlendir
    if (token && isAuthPage) {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }

    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: () => true
    },
  }
);

export const config = {
  matcher: [
    "/signin",
    "/signup", 
    "/dashboard",
    "/first-time",
    "/forgot-password",
    "/profile/:path*",
    "/settings",
    "/chat"
  ]
};
