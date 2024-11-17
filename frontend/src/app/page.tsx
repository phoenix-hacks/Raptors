"use client";

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Header } from "@/sections/Header";
import { Hero } from "@/sections/Hero";
import { Sidebar } from "@/sections/Sidebar";
import { Main } from "@/sections/Main";
import { Footer } from "@/sections/Footer";
import { InfiniteScroll } from "@/sections/InfiniteScroll";

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const checkUserSession = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setIsLoggedIn(!!session);
    };

    checkUserSession();

    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      setIsLoggedIn(!!session);
    });

  }, []);

  return (
    <>
      <Header />
      {isLoggedIn && <Sidebar onSessionSelect={(sessionId: string) => {}} />}
      {isLoggedIn ? <Hero /> : <Main />}
      <Footer />
      <InfiniteScroll />
    </>
  );
}
