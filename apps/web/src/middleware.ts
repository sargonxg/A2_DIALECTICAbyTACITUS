import { NextRequest, NextResponse } from "next/server";

const REALM = "DIALECTICA GraphOps";

function unauthorized() {
  return new NextResponse("Authentication required.", {
    status: 401,
    headers: {
      "WWW-Authenticate": `Basic realm="${REALM}", charset="UTF-8"`,
    },
  });
}

function timingSafeEqual(a: string, b: string) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let index = 0; index < a.length; index += 1) {
    result |= a.charCodeAt(index) ^ b.charCodeAt(index);
  }
  return result === 0;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (
    pathname === "/" ||
    pathname === "/situation-demo" ||
    pathname.startsWith("/situation-demo/") ||
    pathname === "/demo" ||
    pathname.startsWith("/demo/")
  ) {
    return NextResponse.next();
  }

  const username = process.env.GRAPHOPS_BASIC_USER || "tacitus";
  const password = process.env.GRAPHOPS_BASIC_PASSWORD;

  if (!password) {
    return new NextResponse("GRAPHOPS_BASIC_PASSWORD is not configured.", { status: 503 });
  }

  const header = request.headers.get("authorization");
  if (!header?.startsWith("Basic ")) return unauthorized();

  const encoded = header.slice("Basic ".length);
  const decoded = atob(encoded);
  const separator = decoded.indexOf(":");
  if (separator === -1) return unauthorized();

  const suppliedUser = decoded.slice(0, separator);
  const suppliedPassword = decoded.slice(separator + 1);

  if (
    timingSafeEqual(suppliedUser, username) &&
    timingSafeEqual(suppliedPassword, password)
  ) {
    return NextResponse.next();
  }

  return unauthorized();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|og-image.png).*)"],
};
