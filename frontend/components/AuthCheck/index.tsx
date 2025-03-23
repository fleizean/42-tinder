'use client';

import { useEffect, useState } from 'react';
import { useSession, signOut } from 'next-auth/react';
import { usePathname } from 'next/navigation';
import { toast } from 'react-hot-toast';

const AuthCheck = () => {
  const { data: session, update } = useSession();
  const pathname = usePathname();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastRefreshTime, setLastRefreshTime] = useState(0);

  useEffect(() => {
    const checkSession = async () => {
      if (!session?.user?.expiration) return;
      
      const expirationTime = new Date(session.user.expiration).getTime();
      const currentTime = Date.now();
      const timeUntilExpiration = expirationTime - currentTime;
      
      // Prevent refresh more than once every 5 minutes
      const timeSinceLastRefresh = currentTime - lastRefreshTime;
      if (timeSinceLastRefresh < 300000 && lastRefreshTime !== 0) {
        return;
      }
      
      // If token will expire in less than 5 minutes (300,000 ms), refresh it
      if (timeUntilExpiration < 300000 && timeUntilExpiration > 0 && !isRefreshing) {
        setIsRefreshing(true);
        setLastRefreshTime(currentTime);
        
        try {
          // Use NextAuth's update function to refresh the session
          await update();
          console.log("Session refreshed successfully");
          setIsRefreshing(false);
        } catch (error) {
          console.error('Error refreshing session:', error);
          setIsRefreshing(false);
          
          // Only sign out if the error indicates the refresh token is invalid
          if (error && typeof error === 'object' && 'error' in error && error.error === 'RefreshAccessTokenError') {
            toast.error('Oturum yenilenemedi. Lütfen tekrar giriş yapın.');
            signOut({ redirect: true, callbackUrl: '/signin' });
          }
        }
      }
      
      // If token has already expired, sign out
      if (currentTime >= expirationTime && !isRefreshing) {
        toast.error('Oturum süreniz doldu. Lütfen tekrar giriş yapın.');
        signOut({ redirect: true, callbackUrl: '/signin' });
      }
    };

    // Initial check
    checkSession();
    
    // Set up interval, but make it less frequent
    const interval = setInterval(checkSession, 120000); // Check every 2 minutes

    return () => clearInterval(interval);
  }, [session, update, isRefreshing, lastRefreshTime]);

  return null;
};

export default AuthCheck;