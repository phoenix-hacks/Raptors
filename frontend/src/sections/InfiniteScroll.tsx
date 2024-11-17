"use client";

import { motion } from 'framer-motion';
import { useTheme } from '@/Context/ThemeContext';



export const InfiniteScroll = () => {
    const { theme }=useTheme();
    return (
        
        <div className="py-2 lg:py-4 overflow-hidden">
            <div className="flex flex-1 items-center justify-between overflow-hidden">
                <motion.div
                    initial={{ translateX: '-50%' }}
                    animate={{ translateX: '0%' }}
                    transition={{ duration: 240, repeat: Infinity, ease: 'linear' }}
                    className="flex flex-none items-center justify-between whitespace-nowrap -translate-x-1/2">
                    <nav className={`text-8xl md:text-[144px] tracking-tight font-bold ${theme === 'dark' ? 'text-scroll-color' : 'text-gray-200'}  mr-10 pb-4`}>
                        <span>CarbonCare · CarbonCare · CarbonCare · CarbonCare · </span>
                        <span>CarbonCare · CarbonCare · CarbonCare · CarbonCare · </span>
                        <span>CarbonCare · CarbonCare · CarbonCare · CarbonCare · </span>
                        <span>CarbonCare · CarbonCare · CarbonCare · CarbonCare · </span>
                        <span>CarbonCare · CarbonCare · CarbonCare · CarbonCare · </span>
                    </nav>
                </motion.div>
            </div>
        </div>
    );
};
