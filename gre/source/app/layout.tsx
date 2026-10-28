import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = {title:"GRE Vocabulary Master",description:"Private vocabulary practice with daily mixed quizzes and progress across devices."};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}</body></html>;}
