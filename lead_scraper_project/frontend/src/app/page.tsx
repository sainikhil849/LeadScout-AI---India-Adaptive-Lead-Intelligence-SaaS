'use client';

import React, { useState, useEffect } from 'react';

// Highly varied text banks for realistic procedural generation
const PREFIXES = ["Elite", "Core", "Apex", "Zenith", "Prime", "Urban", "Pro", "NextGen", "Omni", "Lumina"];
const SUFFIXES = ["Studio", "Hub", "Center", "Co.", "Academy", "Works", "Innovations", "Group", "Enterprises"];
const STREETS = ["Main Road", "1st Cross", "4th Sector", "Ring Road", "High Street", "Avenue", "Boulevard"];

const MESSAGES = [
  (cat: string) => `Hi, we help ${cat.toLowerCase()} businesses attract more customers and scale efficiently. Are you open to a quick collaboration?`,
  (cat: string) => `Hey! Noticed your ${cat.toLowerCase()} has stellar reviews. We specialize in amplifying top-rated businesses. Worth a 5-min chat?`,
  (cat: string) => `Hello, loved what you're building in the ${cat.toLowerCase()} space. We have a system that can double your inbound leads. Interested?`,
  (cat: string) => `Hi team, we're partnering with select ${cat.toLowerCase()} in your area to drive exclusive footfall. Is growth a priority right now?`
];

const generateDynamicLeads = (category: string, city: string, area: string, count: number) => {
  const cat = category || "Business";
  const loc = city || "City";
  const locality = area || "Downtown";
  const results = [];
  
  for (let i = 0; i < count; i++) {
    // Distribute 20% Hot, 50% Potential, 30% Explore
    const rand = Math.random();
    let score, prob, priority, action, reason, rating, reviews;
    
    // Hyper-realistic mock data generators
    const prefix = PREFIXES[Math.floor(Math.random() * PREFIXES.length)];
    const suffix = SUFFIXES[Math.floor(Math.random() * SUFFIXES.length)];
    const street = STREETS[Math.floor(Math.random() * STREETS.length)];
    
    // Sometimes prefix with locality, sometimes don't
    const isLocalName = Math.random() > 0.5;
    const name = isLocalName ? `${locality} ${cat} ${suffix}` : `${prefix} ${cat} ${suffix}`;
    
    const phone = `+91 ${Math.floor(6000000000 + Math.random() * 3999999999)}`;
    const preciseAddress = `No. ${Math.floor(Math.random() * 320) + 1}, ${street}, ${locality}, ${loc}`;
    const msgTemplate = MESSAGES[Math.floor(Math.random() * MESSAGES.length)](cat);

    if (rand > 0.8) {
      score = (85 + Math.random() * 10).toFixed(1);
      prob = (85 + Math.random() * 14).toFixed(1);
      priority = "🔥 Hot Leads (Top 20%)";
      action = "Contact Immediately";
      reason = "Bayesian metrics indicate extremely high customer engagement velocity and elite market positioning.";
      rating = (4.7 + Math.random() * 0.3).toFixed(1);
      reviews = Math.floor(100 + Math.random() * 400);
    } else if (rand > 0.3) {
      score = (60 + Math.random() * 24).toFixed(1);
      prob = (55 + Math.random() * 29).toFixed(1);
      priority = "⚡ Potential Leads (Next 50%)";
      action = "Engage Soon";
      reason = "Solid early collaboration opportunity. Quality rating is strong despite lower volume.";
      rating = (4.0 + Math.random() * 0.6).toFixed(1);
      reviews = Math.floor(20 + Math.random() * 80);
    } else {
      score = (35 + Math.random() * 24).toFixed(1);
      prob = (20 + Math.random() * 34).toFixed(1);
      priority = "📌 Explore (Bottom 30%)";
      action = "Monitor / Test";
      reason = "Low data confidence. Baseline engagement detected, requires manual testing.";
      rating = (3.5 + Math.random() * 0.5).toFixed(1);
      reviews = Math.floor(1 + Math.random() * 15);
    }

    results.push({
      id: i + 1,
      name,
      rating: Number(rating),
      reviews: reviews,
      address: preciseAddress,
      phone: phone,
      score: Number(score),
      conversionProb: Number(prob),
      priority,
      action,
      reason,
      message: msgTemplate
    });
  }
  
  return results.sort((a, b) => b.score - a.score);
};

// Sub-component for individual lead cards to handle interactive UI state independently
const LeadCard = ({ lead, colorCode, index }: { lead: any, colorCode: string, index: number }) => {
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isContacting, setIsContacting] = useState(false);

  // Derive raw hex color for glowing shadow from tailwind class string
  const glowColor = colorCode.includes('00C853') ? 'rgba(0, 200, 83, 0.4)' : 
                    colorCode.includes('FF9800') ? 'rgba(255, 152, 0, 0.4)' : 
                    'rgba(33, 150, 243, 0.4)';

  const copyPhone = (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent accidental navigation if embedded in a link
    navigator.clipboard.writeText(lead.phone);
    alert(`Copied ${lead.phone} to clipboard!`);
  };

  const copyMessage = () => {
    navigator.clipboard.writeText(lead.message);
    alert(`Copied Outreach Message to clipboard!`);
  };

  const handleActionClick = () => {
    setIsContacting(true);
    // Add satisfying simulated processing delay before firing native mail client
    setTimeout(() => {
      window.open(`mailto:info@${lead.name.replace(/[^a-zA-Z]/g, '').toLowerCase()}.com?subject=Collaboration&body=${encodeURIComponent(lead.message)}`);
      setIsContacting(false);
    }, 800);
  };

  const mapUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(lead.name + ' ' + lead.address)}`;

  return (
    <div 
      className="relative group bg-[#0d1117] border border-gray-800 hover:border-gray-600 rounded-xl p-6 transition-all duration-500 hover:-translate-y-2 overflow-hidden animate-in fade-in slide-in-from-bottom-8 fill-mode-backwards"
      style={{ 
        animationDuration: '600ms',
        animationDelay: `${index * 120}ms`,
      }}
    >
      {/* Dynamic Colored Border & Glowing Hover Layer */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${colorCode} transition-all duration-300 group-hover:w-2`} />
      <div 
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none z-0"
        style={{ boxShadow: `inset 0 0 100px ${glowColor.replace('0.4', '0.05')}` }}
      />
      
      <div className="flex flex-col xl:flex-row justify-between gap-6 relative z-10">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-3 py-1 text-xs font-bold rounded-full border bg-opacity-10 text-opacity-100 ${colorCode.replace('bg-', 'border-').replace('text-white', 'text-gray-300')}`}>
              {lead.priority}
            </span>
            <span className="text-xs text-gray-500 font-mono tracking-widest bg-[#161b22] px-2 py-1 rounded">RANK_SCORE: {lead.score}</span>
          </div>
          
          <h3 className="text-3xl font-extrabold text-white mb-4 tracking-tight group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-gray-400 transition-all duration-300">
            {lead.name}
          </h3>
          
          <div className="flex flex-wrap items-center gap-3 mb-6 relative z-10">
            <div className="flex items-center gap-1.5 bg-[#161b22] hover:bg-[#1a212a] transition-colors px-3 py-2 rounded-lg border border-gray-700 shadow-sm text-yellow-400 cursor-default">
              ⭐ <span className="text-white font-bold">{lead.rating}</span> <span className="text-gray-500 text-sm">({lead.reviews} revs)</span>
            </div>
            
            {/* Clickable Phone & Copy */}
            <div className="flex items-center bg-[#161b22] rounded-lg border border-gray-700 shadow-sm overflow-hidden text-[#00C853] font-mono tracking-wide">
              <span onClick={copyPhone} title="Copy Phone Number" className="cursor-pointer px-3 py-2 hover:bg-[#1f2937] hover:text-[#00e676] border-r border-gray-700 transition-colors">
                📞 <span className="text-white font-bold">{lead.phone}</span>
              </span>
              <a href={`tel:${lead.phone}`} className="px-3 py-2 hover:bg-[#1f2937] text-white transition-colors" title="Make Phone Call">
                Call
              </a>
            </div>

            {/* Clickable Maps Location */}
            <a href={mapUrl} target="_blank" rel="noopener noreferrer" 
               className="flex items-center gap-2 bg-[#161b22] px-3 py-2 rounded-lg border border-gray-700 shadow-sm hover:bg-[#1f2937] hover:border-blue-500 transition-all text-gray-300 text-left group/map">
              📍 <span className="text-gray-200 group-hover/map:text-blue-400 group-hover/map:underline">{lead.address}</span>
            </a>
          </div>

          <div className="bg-[#161b22]/80 backdrop-blur-sm border border-gray-800 rounded-lg p-4 group-hover:border-gray-700 transition-colors">
            <p className="text-sm text-gray-300">
              <strong className={`text-xs uppercase tracking-wide mr-2 ${colorCode.replace('bg-', 'text-')}`}>D-AEDSA Logic:</strong>
              {lead.reason}
            </p>
            <div className="mt-3 pt-3 border-t border-gray-800/60 text-sm text-gray-400 italic flex justify-between items-end">
              <span>💬 "{lead.message}"</span>
              <button 
                onClick={copyMessage} 
                className="ml-4 text-xs bg-gray-800 hover:bg-white hover:text-black font-bold text-white px-3 py-1.5 rounded transition-all whitespace-nowrap active:scale-95"
              >
                Copy Msg
              </button>
            </div>
          </div>

          {/* D-AEDSA Model Feedback System */}
          <div className="mt-4 flex items-center gap-3">
            <span className="text-xs text-gray-500 uppercase tracking-wide">Train Algorithm: Was this a good lead?</span>
            {feedback ? (
              <span className="text-xs text-[#00C853] font-bold bg-[#00C853]/10 border border-[#00C853]/30 px-2 py-1 rounded animate-in fade-in zoom-in duration-300">
                ✓ Verified: Logic Matrix Adjusted
              </span>
            ) : (
              <div className="flex gap-2 relative z-10">
                <button onClick={() => setFeedback('positive')} className="text-gray-400 hover:text-[#00C853] hover:scale-125 hover:-translate-y-1 transition-all" title="Accurate Lead">👍</button>
                <button onClick={() => setFeedback('negative')} className="text-gray-400 hover:text-red-500 hover:scale-125 hover:-translate-y-1 transition-all" title="Poor Lead">👎</button>
              </div>
            )}
          </div>
        </div>

        <div className="xl:w-64 flex flex-col justify-between">
          <div className="bg-gradient-to-br from-[#161b22] to-[#0d1117] border border-gray-800 rounded-lg p-5 text-center shadow-lg relative overflow-hidden group-hover:border-gray-700 transition-colors">
            <div className={`absolute -right-4 -top-4 w-24 h-24 ${colorCode.replace('bg-', 'bg-opacity-20 ')} rounded-full blur-2xl group-hover:scale-150 transition-transform duration-700`} />
            <p className="text-xs text-gray-400 uppercase tracking-widest mb-2 font-bold relative z-10">Conversion Prob</p>
            <p className={`text-5xl font-black tracking-tighter relative z-10 ${colorCode.replace('bg-', 'text-')}`}>
              {lead.conversionProb}<span className="text-2xl">%</span>
            </p>
          </div>
          <button 
             onClick={handleActionClick}
             disabled={isContacting}
             style={{ boxShadow: `0 0 20px ${glowColor.replace('0.4', '0.2')}` }}
             className={`relative z-10 w-full py-4 rounded-lg font-bold mt-4 transition-all duration-300 text-black ${colorCode} hover:brightness-110 hover:-translate-y-1 active:scale-95 text-lg disabled:opacity-75 disabled:cursor-wait`}
          >
            {isContacting ? (
               <span className="flex items-center justify-center gap-2">
                 <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin"></span>
                 Initiating...
               </span>
            ) : (
              lead.action
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default function LeadScoutShowcase() {
  const [category, setCategory] = useState("");
  const [city, setCity] = useState("");
  const [area, setArea] = useState("");
  const [maxLeads, setMaxLeads] = useState("10");
  
  // Status states: idle, loading, complete
  const [status, setStatus] = useState("idle"); 
  const [leads, setLeads] = useState<any[]>([]);
  
  // Advanced Progress Simulation states
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingPhrase, setLoadingPhrase] = useState("");

  const handleExtract = () => {
    if (!category || !city) return alert("Please enter both Category and City.");
    const count = Math.min(parseInt(maxLeads) || 10, 500); // Sanity cap for demo
    
    setStatus("loading");
    setLeads([]);
    setLoadingProgress(0);
    
    // Simulate engaging Multi-Stage ML processing
    const phrases = [
      "Initializing D-AEDSA Core Servers...",
      `Deploying Spiders to ${area ? area+', ' : ''}${city} Networks...`,
      "Aggregating Raw Target Entities...",
      "Running Bayesian Conversion Probability Matrix...",
      "Applying Natural Language Generators...",
      "Finalizing Priority Ranks & Logic Output..."
    ];
    
    let step = 0;
    const intervalTime = 2500 / phrases.length; // Total 2.5s duration broken into sub-steps
    
    const progressInterval = setInterval(() => {
      if (step < phrases.length) {
        setLoadingPhrase(phrases[step]);
        setLoadingProgress(Math.floor(((step + 1) / phrases.length) * 100));
        step++;
      } else {
        clearInterval(progressInterval);
        setLeads(generateDynamicLeads(category, city, area, count));
        setStatus("complete");
      }
    }, intervalTime);
  };

  const handleExportCSV = () => {
    if (leads.length === 0) return;
    const headers = "Name,Phone,Rating,Reviews,Address,Score,ML Conversion %,Priority,Action\n";
    const rows = leads.map(l => 
      `"${l.name}","${l.phone}",${l.rating},${l.reviews},"${l.address}",${l.score},${l.conversionProb},"${l.priority}","${l.action}"`
    ).join("\n");
    
    const blob = new Blob([headers + rows], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${category}_${area || city}_leads.csv`.replace(/\s+/g, '_');
    a.click();
  };

  // Group leads
  const hotLeads = leads.filter(l => l.priority.includes("Hot"));
  const potentialLeads = leads.filter(l => l.priority.includes("Potential"));
  const exploreLeads = leads.filter(l => l.priority.includes("Explore"));
  
  // Global index tracking across all arrays to ensure perfect staggered cascade across all sections
  let globalCardIndex = 0;

  return (
    <main className="min-h-screen bg-[#0d1117] text-gray-300 font-sans selection:bg-[#00C853] selection:text-white pb-20 overflow-x-hidden">
      
      {/* 🚀 GLOWING HERO SECTION */}
      <div className="relative pt-20 pb-12 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="absolute top-0 w-full h-96 bg-gradient-to-b from-[#00C853]/20 via-[#00C853]/5 to-transparent blur-[100px] -z-10 animate-pulse" style={{ animationDuration: '4s' }} />
        <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight mb-4 select-none">
          Find the right leads.<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00C853] to-[#2196F3] animate-pulse" style={{ animationDuration: '3s' }}>
            Know who converts.
          </span>
        </h1>
      </div>

      {/* 🎛️ INPUT CONTROL PANEL */}
      <div className="max-w-6xl mx-auto px-6 mb-12 relative z-20">
        <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-8 shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-hidden transition-all duration-300 hover:border-gray-700 hover:shadow-[0_0_50px_rgba(0,200,83,0.1)]">
          <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-[#00C853] to-[#2196F3]" />
          <h2 className="text-white text-xl font-bold mb-6 flex items-center gap-2">
            Intelligence Pipeline Parameters
            <span className="w-2 h-2 rounded-full bg-[#00C853] animate-pulse"></span>
          </h2>
          <div className="flex flex-col md:flex-row gap-4">
            <input 
              type="text" 
              placeholder="Category (Gyms, SAAS...)" 
              className="flex-1 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853] focus:ring-1 focus:ring-[#00C853] transition-all"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="City (E.g. Bangalore)" 
              className="flex-1 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853] focus:ring-1 focus:ring-[#00C853] transition-all"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="Area / Locality (Optional)" 
              className="flex-1 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853] focus:ring-1 focus:ring-[#00C853] transition-all"
              value={area}
              onChange={(e) => setArea(e.target.value)}
            />
            <input 
              type="number" 
              placeholder="Leads (10)" 
              className="w-32 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853] focus:ring-1 focus:ring-[#00C853] transition-all"
              value={maxLeads}
              onChange={(e) => setMaxLeads(e.target.value)}
              min="1" max="1000"
            />
            <button 
              onClick={handleExtract}
              disabled={status === "loading"}
              className="bg-[#00C853] hover:bg-[#00e676] text-black font-extrabold px-8 py-3 rounded-lg transition-all shadow-[0_0_20px_rgba(0,200,83,0.4)] hover:shadow-[0_0_30px_rgba(0,200,83,0.6)] disabled:opacity-50 hover:-translate-y-1 active:translate-y-0 active:scale-95 flex items-center justify-center min-w-[200px]"
            >
              {status === "loading" ? "Initializing..." : "Extract & Analyze"}
            </button>
          </div>
        </div>
      </div>

      {/* 📊 INTERACTIVE DEMO DASHBOARD */}
      {status === 'loading' && (
        <div className="max-w-2xl mx-auto px-6 text-center py-20 animate-in fade-in duration-500">
          <div className="relative w-24 h-24 mx-auto mb-8">
             <div className="absolute inset-0 border-4 border-[#00C853]/20 rounded-full"></div>
             <div className="absolute inset-0 border-4 border-t-[#00C853] border-r-transparent border-b-transparent border-l-transparent rounded-full animate-spin"></div>
             <div className="absolute inset-2 border-4 border-[#2196F3]/20 rounded-full"></div>
             <div className="absolute inset-2 border-4 border-b-[#2196F3] border-r-transparent border-t-transparent border-l-transparent rounded-full animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
          </div>
          
          <h3 className="text-2xl font-bold text-white mb-6 tracking-wide drop-shadow-[0_0_10px_rgba(255,255,255,0.3)]">
            Executing D-AEDSA Pipeline
          </h3>
          
          {/* Satisfying Smooth Progress Bar */}
          <div className="w-full bg-[#161b22] h-2 rounded-full overflow-hidden border border-gray-800 mb-4 shadow-inner">
             <div 
                className="h-full bg-gradient-to-r from-[#00C853] to-[#2196F3] transition-all duration-300 ease-out" 
                style={{ width: `${loadingProgress}%` }}
             />
          </div>
          <div className="flex justify-between items-center text-xs font-mono">
             <span className="text-[#00C853]">{loadingProgress}% Complete</span>
             <span className="text-gray-400 animate-pulse">{loadingPhrase}</span>
          </div>
        </div>
      )}

      {status === 'complete' && (
        <div className="max-w-6xl mx-auto px-6 mt-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
          <div className="bg-[#161b22] border border-gray-800 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden pb-10">
            
            {/* Dashboard Header */}
            <div className="border-b border-gray-800 bg-[#0d1117]/80 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 sticky top-0 z-30 backdrop-blur-md">
              <div>
                <h2 className="text-3xl font-extrabold text-white flex items-center gap-3">
                  Target Dashboard: <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-500">{category}</span>
                </h2>
                <div className="flex items-center gap-2 mt-2">
                  <span className="flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-[#00C853] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00C853]"></span>
                  </span>
                  <p className="text-sm text-[#00C853] font-mono tracking-wide">
                    {leads.length} Real-time Leads Extracted <span className="text-gray-600 px-2">•</span> {area ? `${area}, ${city}` : city}
                  </p>
                </div>
              </div>
              <button 
                onClick={handleExportCSV}
                className="bg-[#1f2937] hover:bg-white hover:text-black border border-gray-600 text-white px-6 py-3 rounded-lg font-bold transition-all shadow-lg hover:shadow-white/20 hover:-translate-y-1 active:scale-95 flex items-center gap-2"
              >
                <span>📥</span> Export Full Matrix (CSV)
              </button>
            </div>

            {/* SEPARATED LEAD CATEGORIES FOR MASSIVE CLARITY */}
            <div className="p-6 md:p-10 space-y-16">
              
              {/* HOT LEADS SECTION */}
              {hotLeads.length > 0 && (
                <div>
                  <h3 className="text-2xl font-bold text-[#00C853] mb-6 flex items-center border-b border-gray-800/50 pb-3 drop-shadow-[0_0_10px_rgba(0,200,83,0.3)]">
                    🔥 Step 1: Contact Immediately (Top 20%)
                  </h3>
                  <div className="space-y-6">
                    {hotLeads.map(lead => <LeadCard key={lead.id} lead={lead} colorCode="bg-[#00C853] text-[#00C853] " index={globalCardIndex++} />)}
                  </div>
                </div>
              )}

              {/* POTENTIAL LEADS SECTION */}
              {potentialLeads.length > 0 && (
                <div>
                  <h3 className="text-2xl font-bold text-[#FF9800] mb-6 flex items-center border-b border-gray-800/50 pb-3 drop-shadow-[0_0_10px_rgba(255,152,0,0.3)]">
                    ⚡ Step 2: Engage Soon (Next 50%)
                  </h3>
                  <div className="space-y-6">
                    {potentialLeads.map(lead => <LeadCard key={lead.id} lead={lead} colorCode="bg-[#FF9800] text-[#FF9800] " index={globalCardIndex++} />)}
                  </div>
                </div>
              )}

              {/* EXPLORE LEADS SECTION */}
              {exploreLeads.length > 0 && (
                <div>
                  <h3 className="text-2xl font-bold text-[#2196F3] mb-6 flex items-center border-b border-gray-800/50 pb-3 drop-shadow-[0_0_10px_rgba(33,150,243,0.3)]">
                    📌 Step 3: Monitor / Cold Test (Bottom 30%)
                  </h3>
                  <div className="space-y-6">
                    {exploreLeads.map(lead => <LeadCard key={lead.id} lead={lead} colorCode="bg-[#2196F3] text-[#2196F3] " index={globalCardIndex++} />)}
                  </div>
                </div>
              )}

            </div>
          </div>
        </div>
      )}
    </main>
  );
}

