import { NextResponse, type NextRequest } from "next/server";

import { SESSION_COOKIE_NAME, verifySessionToken } from "@/lib/auth/session-token";

const LOGIN_PATH = "/login";

function loginRedirect(request: NextRequest): NextResponse {
  const redirectUrl = new URL(LOGIN_PATH, request.url);
  const nextPath = `${request.nextUrl.pathname}${request.nextUrl.search}`;
  redirectUrl.searchParams.set("next", nextPath);

  const response = NextResponse.redirect(redirectUrl);
  response.cookies.delete(SESSION_COOKIE_NAME);
  return response;
}

export function proxy(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const session = verifySessionToken(request.cookies.get(SESSION_COOKIE_NAME)?.value);
  const isLoginRoute = pathname === LOGIN_PATH;

  if (isLoginRoute && session) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  if (!isLoginRoute && !session) {
    return loginRedirect(request);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:png|jpg|jpeg|gif|svg|webp|ico|css|js|map|txt)$).*)",
  ],
};
