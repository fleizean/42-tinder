'use client';

import { useEffect } from 'react';
import { useSession, signOut } from 'next-auth/react';
import { usePathname } from 'next/navigation';

const AuthCheck = () => {
  const { data: session } = useSession();
  const pathname = usePathname();

  useEffect(() => {
    const checkSession = () => {
      if (session?.user?.expiration) {
        const expirationTime = new Date(session.user.expiration).getTime();
        if (Date.now() >= expirationTime) {
          signOut({ redirect: true, callbackUrl: '/signin' });
        }
      }
    };

    checkSession();
    const interval = setInterval(checkSession, 60000); // Check every minute

    return () => clearInterval(interval);
  }, [session]);

  return null;
};

export default AuthCheck;