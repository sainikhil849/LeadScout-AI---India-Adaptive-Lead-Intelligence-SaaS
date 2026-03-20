'use client';

import React, { useState } from 'react';

// Generates dynamic mock data based on user input
const generateDynamicLeads = (category: string, city: string, area: string, count: number) => {
  const cat = category || "Business";
  const loc = city || "City";
  const locality = area || "Downtown";
  const results = [];
  
  for (let i = 0; i < count; i++) {
    // Distribute 20% Hot, 50% Potential, 30% Explore
    const rand = Math.random();
    let score, prob, priority, action, reason, name, rating, reviews;
    
    // Generate realistic Indian phone numbers
    const phone = `+91 ${Math.floor(6000000000 + Math.random() * 3999999999)}`;
    // Generate precise address using Area & City
    const preciseAddress = `No. ${Math.floor(Math.random() * 320) + 1}, ${locality}, ${loc}`;
    
    if (rand > 0.8) {
      score = (85 + Math.random() * 10).toFixed(1);
      prob = (85 + Math.random() * 14).toFixed(1);
      priority = "🔥 Hot Leads (Top 20%)";
      action = "Contact Immediately";
      reason = "Bayesian metrics indicate extremely high customer engagement velocity.";
      name = `Premium ${cat} Center`;
      rating = (4.7 + Math.random() * 0.3).toFixed(1);
      reviews = Math.floor(100 + Math.random() * 400);
    } else if (rand > 0.3) {
      score = (60 + Math.random() * 24).toFixed(1);
      prob = (55 + Math.random() * 29).toFixed(1);
      priority = "⚡ Potential Leads (Next 50%)";
      action = "Engage Soon";
      reason = "Solid early collaboration opportunity. Quality rating is strong.";
      name = `The ${loc} ${cat} Hub`;
      rating = (4.0 + Math.random() * 0.6).toFixed(1);
      reviews = Math.floor(20 + Math.random() * 80);
    } else {
      score = (35 + Math.random() * 24).toFixed(1);
      prob = (20 + Math.random() * 34).toFixed(1);
      priority = "📌 Explore (Bottom 30%)";
      action = "Monitor / Test";
      reason = "Low data confidence. Baseline engagement detected.";
      name = `Local ${cat} Co.`;
      rating = (3.5 + Math.random() * 0.5).toFixed(1);
      reviews = Math.floor(1 + Math.random() * 15);
    }

    results.push({
      id: i + 1,
      name: `${name} #${Math.floor(Math.random() * 1000)}`,
      rating: Number(rating),
      reviews: reviews,
      address: preciseAddress,
      phone: phone,
      score: Number(score),
      conversionProb: Number(prob),
      priority,
      action,
      reason,
      message: `Hi, we help ${cat.toLowerCase()} businesses attract more customers. Open to a quick collaboration?`
    });
  }
  
  return results.sort((a, b) => b.score - a.score);
};

export default function LeadScoutShowcase() {
  const [category, setCategory] = useState("");
  const [city, setCity] = useState("");
  const [area, setArea] = useState("");
  const [maxLeads, setMaxLeads] = useState("10");
  const [status, setStatus] = useState("idle"); // idle, loading, complete
  const [leads, setLeads] = useState<any[]>([]);

  const handleExtract = () => {
    if (!category || !city) return alert("Please enter both Category and City.");
    const count = parseInt(maxLeads) || 10;
    
    setStatus("loading");
    setLeads([]);
    
    // Simulate ML processing
    setTimeout(() => {
      setLeads(generateDynamicLeads(category, city, area, count));
      setStatus("complete");
    }, 2500);
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

  // Group leads for immense visual clarity ensuring the user knows exactly who to contact
  const hotLeads = leads.filter(l => l.priority.includes("Hot"));
  const potentialLeads = leads.filter(l => l.priority.includes("Potential"));
  const exploreLeads = leads.filter(l => l.priority.includes("Explore"));

  const renderLeadCard = (lead: any, colorCode: string) => (
    <div key={lead.id} className="relative group bg-[#0d1117] border border-gray-800 hover:border-gray-600 rounded-xl p-6 transition-all duration-300 hover:shadow-2xl overflow-hidden">
      {/* Dynamic Colored Border */}
      <div className={`absolute left-0 top-0 bottom-0 w-1 ${colorCode}`} />
      
      <div className="flex flex-col xl:flex-row justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-4">
            <span className={`px-3 py-1 text-xs font-bold rounded-full border bg-opacity-10 text-opacity-100 ${colorCode.replace('bg-', 'border-').replace('text-white', 'text-gray-300')}`}>
              {lead.priority}
            </span>
            <span className="text-xs text-gray-500 font-mono tracking-widest">RANK_SCORE: {lead.score}</span>
          </div>
          
          <h3 className="text-3xl font-extrabold text-white mb-4 tracking-tight">{lead.name}</h3>
          
          {/* HIGH CLARITY BADGES (Rating, Phone, Location) */}
          <div className="flex flex-wrap items-center gap-3 mb-6">
            <div className="flex items-center gap-1.5 bg-[#161b22] px-3 py-2 rounded-lg border border-gray-700 shadow-sm text-yellow-400">
              ⭐ <span className="text-white font-bold">{lead.rating}</span> <span className="text-gray-500 text-sm">({lead.reviews} revs)</span>
            </div>
            <div className="flex items-center gap-2 bg-[#161b22] px-3 py-2 rounded-lg border border-gray-700 shadow-sm text-[#00C853] font-mono tracking-wide">
              📞 <span className="text-white font-bold">{lead.phone}</span>
            </div>
            <div className="flex items-center gap-2 bg-[#161b22] px-3 py-2 rounded-lg border border-gray-700 shadow-sm text-gray-300 break-words whitespace-normal text-left">
              📍 <span className="text-gray-200">{lead.address}</span>
            </div>
          </div>

          <div className="bg-[#161b22] border border-gray-800 rounded-lg p-4">
            <p className="text-sm text-gray-300">
              <strong className={`text-xs uppercase tracking-wide mr-2 ${colorCode.replace('bg-', 'text-')}`}>D-AEDSA Logic:</strong>
              {lead.reason}
            </p>
            <div className="mt-3 pt-3 border-t border-gray-800 text-sm text-gray-400 italic">
              💬 "{lead.message}"
            </div>
          </div>
        </div>

        <div className="xl:w-64 flex flex-col justify-between">
          <div className="bg-gradient-to-br from-[#161b22] to-[#0d1117] border border-gray-800 rounded-lg p-5 text-center shadow-lg relative overflow-hidden">
            <div className={`absolute -right-4 -top-4 w-16 h-16 ${colorCode.replace('bg-', 'bg-opacity-20 ')} rounded-full blur-xl`} />
            <p className="text-xs text-gray-400 uppercase tracking-widest mb-2 font-bold">Conversion Prob</p>
            <p className={`text-5xl font-black tracking-tighter ${colorCode.replace('bg-', 'text-')}`}>
              {lead.conversionProb}<span className="text-2xl">%</span>
            </p>
          </div>
          <button className={`w-full py-4 rounded-lg font-bold mt-4 transition-all shadow-lg text-black ${colorCode} hover:opacity-80 text-lg`}>
            {lead.action}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <main className="min-h-screen bg-[#0d1117] text-gray-300 font-sans selection:bg-[#00C853] selection:text-white pb-20">
      
      {/* 🚀 GLOWING HERO SECTION */}
      <div className="relative pt-20 pb-12 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="absolute top-0 w-full h-96 bg-gradient-to-b from-[#00C853]/20 to-transparent blur-3xl -z-10" />
        <h1 className="text-5xl md:text-7xl font-extrabold text-white tracking-tight mb-4">
          Find the right leads.<br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-[#00C853] to-[#2196F3]">
            Know who converts.
          </span>
        </h1>
      </div>

      {/* 🎛️ INPUT CONTROL PANEL */}
      <div className="max-w-6xl mx-auto px-6 mb-12">
        <div className="bg-[#161b22] border border-gray-800 rounded-2xl p-8 shadow-2xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-[#00C853]" />
          <h2 className="text-white text-xl font-bold mb-6">Intelligence Pipeline Parameters</h2>
          <div className="flex flex-col md:flex-row gap-4">
            <input 
              type="text" 
              placeholder="Category (Gyms, SAAS...)" 
              className="flex-1 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853]"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="City (E.g. Bangalore)" 
              className="flex-1 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853]"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
            <input 
              type="text" 
              placeholder="Area / Locality (Optional)" 
              className="flex-1 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853]"
              value={area}
              onChange={(e) => setArea(e.target.value)}
            />
            <input 
              type="number" 
              placeholder="Leads (e.g. 10)" 
              className="w-32 bg-[#0d1117] border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-[#00C853]"
              value={maxLeads}
              onChange={(e) => setMaxLeads(e.target.value)}
              min="1" max="100"
            />
            <button 
              onClick={handleExtract}
              disabled={status === "loading"}
              className="bg-[#00C853] hover:bg-[#00e676] text-black font-extrabold px-8 py-3 rounded-lg transition-all shadow-[0_0_15px_rgba(0,200,83,0.3)] disabled:opacity-50"
            >
              {status === "loading" ? "Scraping UI..." : "Extract & Analyze"}
            </button>
          </div>
        </div>
      </div>

      {/* 📊 INTERACTIVE DEMO DASHBOARD */}
      {status === 'loading' && (
        <div className="max-w-4xl mx-auto px-6 text-center py-20">
          <div className="inline-block w-16 h-16 border-4 border-[#00C853]/30 border-t-[#00C853] rounded-full animate-spin mb-6"></div>
          <h3 className="text-2xl font-bold text-white mb-2">Executing D-AEDSA Pipeline...</h3>
          <p className="text-gray-400 font-mono text-sm animate-pulse">Running Geolocation Matrix in {area || city} | Processing up to {maxLeads} targets...</p>
        </div>
      )}

      {status === 'complete' && (
        <div className="max-w-6xl mx-auto px-6 mt-10 animate-in fade-in slide-in-from-bottom-8 duration-700">
          <div className="bg-[#161b22] border border-gray-800 rounded-2xl shadow-2xl overflow-hidden pb-10">
            
            {/* Dashboard Header */}
            <div className="border-b border-gray-800 bg-[#0d1117]/50 p-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 className="text-2xl font-bold text-white">Target Dashboard: {category} in {area ? `${area}, ${city}` : city}</h2>
                <p className="text-sm text-gray-500 mt-1">Live D-AEDSA Extracted Results ({leads.length} leads generated)</p>
              </div>
              <button 
                onClick={handleExportCSV}
                className="bg-[#1f2937] hover:bg-[#374151] border border-gray-600 text-white px-6 py-2 rounded-lg font-semibold transition-all"
              >
                📥 Export Entire Pipeline to CSV
              </button>
            </div>

            {/* SEPARATED LEAD CATEGORIES FOR MASSIVE CLARITY */}
            <div className="p-6 md:p-10 space-y-12">
              
              {/* HOT LEADS SECTION */}
              {hotLeads.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-[#00C853] mb-4 flex items-center border-b border-gray-800 pb-2">
                    🔥 Step 1: Contact Immediately (Top 20%)
                  </h3>
                  <div className="space-y-6">
                    {hotLeads.map(lead => renderLeadCard(lead, 'bg-[#00C853] text-[#00C853] '))}
                  </div>
                </div>
              )}

              {/* POTENTIAL LEADS SECTION */}
              {potentialLeads.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-[#FF9800] mb-4 flex items-center border-b border-gray-800 pb-2">
                    ⚡ Step 2: Engage Soon (Next 50%)
                  </h3>
                  <div className="space-y-6">
                    {potentialLeads.map(lead => renderLeadCard(lead, 'bg-[#FF9800] text-[#FF9800] '))}
                  </div>
                </div>
              )}

              {/* EXPLORE LEADS SECTION */}
              {exploreLeads.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-[#2196F3] mb-4 flex items-center border-b border-gray-800 pb-2">
                    📌 Step 3: Monitor / Cold Test (Bottom 30%)
                  </h3>
                  <div className="space-y-6">
                    {exploreLeads.map(lead => renderLeadCard(lead, 'bg-[#2196F3] text-[#2196F3] '))}
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

