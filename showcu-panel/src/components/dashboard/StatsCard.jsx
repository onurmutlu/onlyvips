import React from 'react';

const StatsCard = ({ title, value, icon, trend = 0, color = "primary" }) => {
  const trendIcon = trend > 0 ? "trending-up" : trend < 0 ? "trending-down" : "trending-neutral";
  const trendColor = trend > 0 ? "success" : trend < 0 ? "error" : "text-muted";
  
  const formattedTrend = Math.abs(trend).toFixed(1);
  
  const colorClass = {
    primary: "bg-primary bg-opacity-10 text-primary border-primary",
    success: "bg-success bg-opacity-10 text-success border-success",
    info: "bg-info bg-opacity-10 text-info border-info",
    warning: "bg-warning bg-opacity-10 text-warning border-warning",
    error: "bg-error bg-opacity-10 text-error border-error",
    accent: "bg-accent bg-opacity-10 text-primary border-accent",
  }[color];
  
  const getIconClass = (iconName) => `i-mdi-${iconName}`;
  
  return (
    <div className="card p-4 border-l-3">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-text-muted text-xs mb-1">{title}</p>
          <p className="text-lg md:text-xl font-semibold">{value}</p>
        </div>
        <div className={`p-2 rounded-full ${colorClass}`}>
          <div className={`${getIconClass(icon)} text-xl`}></div>
        </div>
      </div>
      
      {trend !== 0 && (
        <div className="flex items-center mt-3">
          <div className={`${getIconClass(trendIcon)} text-${trendColor} mr-1`}></div>
          <span className={`text-xs text-${trendColor}`}>
            {formattedTrend}% {trend > 0 ? 'artış' : 'azalış'}
          </span>
        </div>
      )}
    </div>
  );
};

export default StatsCard; 