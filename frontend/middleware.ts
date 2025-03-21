
import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

export default withAuth(
  async function middleware(req) {
    const authPages = ["/signin", "/signup", "/forgot-password"];
    const isAuthPage = authPages.includes(req.nextUrl.pathname);
    const token = req.nextauth?.token;

    // Profile path handling
    if (req.nextUrl.pathname.startsWith('/profile')) {
      const segments = req.nextUrl.pathname.split('/');
      const username = segments[2];

      // Check if path has username
      if (segments.length > 2 && username) {
        if (!token) {
          return NextResponse.redirect(new URL("/signin", req.url));
        }

        try {
          // Check if profile exists
          const profileCheckResponse = await fetch(
            `${process.env.NEXT_AUTH_BACKEND_URL}/api/profiles/check-real-profile/${username}`,
            {
              headers: {
                Authorization: `Bearer ${token.accessToken}`,
              },
            }
          );

          if (!profileCheckResponse.ok) {
            // Profile doesn't exist, redirect to 404
            return NextResponse.redirect(new URL("/404", req.url));
          }

          const result = await profileCheckResponse.json();
          if (!result.exists) {  // API artık { exists: true } döndürüyor
            return NextResponse.redirect(new URL("/404", req.url));
          }
        } catch (error) {
          console.error('Profile check error:', error);
          return NextResponse.redirect(new URL("/404", req.url));
        }
      } else {
        return token 
          ? NextResponse.redirect(new URL("/dashboard", req.url))
          : NextResponse.redirect(new URL("/signin", req.url));
      }
    }

    // Token expiration check
    if ((token?.expiration && Date.now() >= new Date(token.expiration).getTime()) || 
        (!token && !isAuthPage && req.nextUrl.pathname !== "/")) {
      const response = NextResponse.redirect(new URL("/signin", req.url));
      
      response.cookies.delete("next-auth.session-token");
      response.cookies.delete("next-auth.callback-url");
      response.cookies.delete("accessToken");
      
      return response;
    }

    if (token && req.nextUrl.pathname === "/") {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }

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
    "/",
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