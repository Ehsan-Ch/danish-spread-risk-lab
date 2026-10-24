export const sum=a=>a.reduce((s,v)=>s+v,0);
export function exposure(actual,forecast,mw=1){
 if(!Number.isFinite(mw)||mw<0||mw>10||actual.length!==forecast.length||!actual.every(Number.isFinite)||!forecast.every(r=>r.length===3&&r.every(Number.isFinite)&&r[0]<=r[1]&&r[1]<=r[2]))throw Error('Invalid exposure');
 const q=mw*.25;return {mw,mwh:q*actual.length,net_cost:q*sum(actual),absolute_cost:q*sum(actual.map(Math.abs)),forecast_cost:q*sum(forecast.map(r=>r[1])),envelope_lower:q*sum(forecast.map(r=>r[0])),envelope_upper:q*sum(forecast.map(r=>r[2]))};
}
export function dailyCSV(d,reg,prob,mw){
 const rows=[['time_utc','delivery_local','issue_utc','dk1_eur_mwh','dk2_eur_mwh','spread_eur_mwh','forecast_lower','forecast_point','forecast_upper','event_probability','event_actual','alert','mw','actual_cost_eur','forecast_cost_eur']];
 d.times.forEach((t,i)=>rows.push([t,d.labels[i],d.issue,d.dk1[i],d.dk2[i],d.actual[i],...d.regression[reg][i],d.probability[prob][i],Number(Math.abs(d.actual[i])>10),Number(d.probability[prob][i]>=.6),mw,d.actual[i]*mw*.25,d.regression[reg][i][1]*mw*.25]));
 return rows.map(r=>r.join(',')).join('\r\n')+'\r\n';
}
export function reliability(labels,probs){return Array.from({length:10},(_,i)=>{const ids=probs.map((p,j)=>p>=i/10&&(i===9?p<=1:p<(i+1)/10)?j:-1).filter(j=>j>=0);return {bin:i,n:ids.length,predicted:ids.length?sum(ids.map(j=>probs[j]))/ids.length:null,observed:ids.length?sum(ids.map(j=>labels[j]))/ids.length:null};});}
