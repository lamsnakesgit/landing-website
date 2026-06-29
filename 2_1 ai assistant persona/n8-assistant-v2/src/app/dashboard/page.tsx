"use client";

import { ArrowRight, ImageIcon, MessageSquare, Zap } from "lucide-react";
import Link from "next/link";
import { useLanguage } from "@/contexts/LanguageContext";

export default function DashboardPage() {
  const { t } = useLanguage();

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-10 gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2">{t.dashboard.welcome}</h1>
          <p className="text-gray-400">{t.dashboard.subtitle}</p>
        </div>
        
        <div className="glass-panel px-6 py-3 rounded-2xl flex items-center gap-4">
          <div className="flex flex-col">
            <span className="text-xs text-gray-400">{t.dashboard.balance}</span>
            <span className="font-bold text-lg text-blue-400">50 CR</span>
          </div>
          <Link href="/dashboard/billing" className="bg-white/10 hover:bg-white/20 p-2 rounded-xl transition-colors">
            <Zap className="w-4 h-4 text-yellow-400" />
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        {/* Primary Action Card */}
        <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group border border-blue-500/30 hover:border-blue-500/60 transition-colors">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <MessageSquare className="w-32 h-32 text-blue-500" />
          </div>
          <h2 className="text-2xl font-bold mb-3 relative z-10">{t.dashboard.chat_title}</h2>
          <p className="text-gray-400 mb-8 max-w-sm relative z-10">
            {t.dashboard.chat_desc}
          </p>
          <Link 
            href="/dashboard/chat"
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-full font-medium transition-colors relative z-10"
          >
            {t.dashboard.chat_btn}
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* Secondary Action Card */}
        <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group border border-purple-500/30 hover:border-purple-500/60 transition-colors">
          <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
            <ImageIcon className="w-32 h-32 text-purple-500" />
          </div>
          <h2 className="text-2xl font-bold mb-3 relative z-10">{t.dashboard.carousel_title}</h2>
          <p className="text-gray-400 mb-8 max-w-sm relative z-10">
            {t.dashboard.carousel_desc}
          </p>
          <Link 
            href="/dashboard/chat?intent=carousel"
            className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-full font-medium transition-colors relative z-10"
          >
            {t.dashboard.carousel_btn}
            <ImageIcon className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* Recent Activity (Mock) */}
      <div>
        <h3 className="text-xl font-bold mb-6">{t.dashboard.recent_activity}</h3>
        <div className="glass-panel rounded-3xl overflow-hidden">
          <div className="divide-y divide-white/10">
            {[1, 2, 3].map((i) => (
              <div key={i} className="p-4 flex items-center justify-between hover:bg-white/5 transition-colors cursor-pointer">
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <p className="font-medium">{t.dashboard.activity_request}</p>
                    <p className="text-sm text-gray-400">"{t.dashboard.activity_example}"</p>
                  </div>
                </div>
                <span className="text-sm text-gray-500">{t.dashboard.activity_time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
