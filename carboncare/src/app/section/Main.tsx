"use client";

import gridLines from "@/assets/grid-lines.png";
import Spline from "@splinetool/react-spline";
import { motion, useMotionTemplate, useMotionValue, useScroll, useTransform } from "framer-motion";
import { RefObject, useEffect, useRef } from "react";
import { useTheme } from "@/Context/ThemeContext";

const useRelativeMousePosition = (to: RefObject<HTMLElement>) => {
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);
    const updateMousePosition = (event: MouseEvent) => {
        if (!to.current) return;
        const { top, left } = to.current.getBoundingClientRect();
        mouseX.set(event.x - left);
        mouseY.set(event.y - top);
    };
    useEffect(() => {
        window.addEventListener("mousemove", updateMousePosition);
        return () => {
            window.removeEventListener("mousemove", updateMousePosition);
        }
    }, []);
    return [mouseX, mouseY];
};

export const Main = () => {
    const sectionRef = useRef<HTMLElement>(null);
    const borderedDivRef = useRef<HTMLDivElement>(null);
    const { scrollYProgress } = useScroll({
        target: sectionRef,
        offset: ["start end", "end start"],
    });

    const { theme } = useTheme();

    const backgroundPositionY = useTransform(scrollYProgress, [0, 1], [-300, 300]);
    const [mouseX, mouseY] = useRelativeMousePosition(borderedDivRef);
    const maskImage = useMotionTemplate`radial-gradient(50% 50% at ${mouseX}px ${mouseY}px, black, transparent)`;

    return (
        <section ref={sectionRef}>
            <div className="container py-16">
                <div className="max-w-6xl mx-auto space-y-4">
                    <motion.div className={`border py-24 overflow-hidden relative group min-h-[360px] md:min-h-[400px] ${theme === 'dark' ? 'border-white' : 'border-black'}`}
                        style={{
                            backgroundPositionY,
                        }}>
                        <div className="absolute inset-0 bg-primary bg-blend-overlay [mask-image:radial-gradient(50%_50%_at_50%_35%,black,transparent)] group-hover:opacity-0 transition duration-700"
                            style={{
                                backgroundImage: `url(${gridLines.src})`,
                                
                                
                            }}>
                        </div>
                        <motion.div ref={borderedDivRef} className="absolute inset-0 bg-primary bg-blend-overlay opacity-0 group-hover:opacity-100 transition duration-700"
                            style={{
                                maskImage,
                                backgroundImage: `url(${gridLines.src})`,
                                
                            }}>
                        </motion.div>
                        <div className="relative">
                            <h2 className="text-3xl md:text-5xl max-w-lg mx-auto text-center tracking-tighter font-medium">Optimize Your Carbon Footprint, Effortlessly.</h2>
                            <div className="mt-20 md:mt-8">
                                <Spline className="-mb-80 md:-mb-40" scene="https://prod.spline.design/UlZ9qLrac0IAUv3a/scene.splinecode" />
                            </div>
                        </div>
                    </motion.div>
                </div>
            </div >
        </section >
    );
};