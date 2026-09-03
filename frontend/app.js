
const T={
en:{brand:"CIVIC SENSE",detect:"Detect",issues:"Issues",city:"City Pulse",reports:"Reports",hero:"AI POWERED CIVIC INTELLIGENCE",heroText:"See what your city needs. Upload a street image and Civic Sense automatically analyses it for common civic issues.",start:"START DETECTION ↗",detectTitle:"DETECT.",detectSub:"Upload an image and let the browser analyse it automatically.",upload:"DROP AN IMAGE",choose:"CHOOSE IMAGE",analysing:"ANALYSING IMAGE…",ready:"IMAGE READY",result:"ANALYSIS RESULT",noResult:"Upload an image to begin.",map:"CITY MAP",mapSub:"Civic issues near you.",locate:"USE MY LOCATION",reports:"RECENT REPORTS",garbage:"Garbage",pothole:"Pothole",road:"Road Damage",light:"Street Light",water:"Waterlogging"},
hi:{brand:"सिविक सेंस",detect:"पता लगाएं",issues:"समस्याएं",city:"शहर स्थिति",reports:"रिपोर्ट",hero:"AI आधारित नागरिक तकनीक",heroText:"जानें कि आपके शहर को क्या चाहिए। तस्वीर अपलोड करें और सिविक सेंस सामान्य नागरिक समस्याओं का विश्लेषण करेगा।",start:"डिटेक्शन शुरू करें ↗",detectTitle:"पता लगाएं.",detectSub:"तस्वीर अपलोड करें और ब्राउज़र से स्वतः विश्लेषण करें।",upload:"तस्वीर डालें",choose:"तस्वीर चुनें",analysing:"विश्लेषण हो रहा है…",ready:"तस्वीर तैयार",result:"विश्लेषण परिणाम",noResult:"शुरू करने के लिए तस्वीर अपलोड करें।",map:"शहर का नक्शा",mapSub:"आपके पास नागरिक समस्याएं।",locate:"मेरी लोकेशन",reports:"हाल की रिपोर्ट",garbage:"कचरा",pothole:"गड्ढा",road:"सड़क क्षति",light:"स्ट्रीट लाइट",water:"जलभराव"},
mr:{brand:"सिविक सेन्स",detect:"शोधा",issues:"समस्या",city:"शहर स्थिती",reports:"अहवाल",hero:"AI आधारित नागरी तंत्रज्ञान",heroText:"तुमच्या शहराला काय हवे आहे ते पहा. प्रतिमा अपलोड करा आणि सिविक सेन्स सामान्य नागरी समस्या आपोआप तपासेल.",start:"डिटेक्शन सुरू करा ↗",detectTitle:"शोधा.",detectSub:"प्रतिमा अपलोड करा आणि ब्राउझर आपोआप विश्लेषण करेल.",upload:"प्रतिमा टाका",choose:"प्रतिमा निवडा",analysing:"विश्लेषण सुरू आहे…",ready:"प्रतिमा तयार",result:"विश्लेषण परिणाम",noResult:"सुरू करण्यासाठी प्रतिमा अपलोड करा.",map:"शहर नकाशा",mapSub:"तुमच्या जवळील नागरी समस्या.",locate:"माझे स्थान",reports:"अलीकडील अहवाल",garbage:"कचरा",pothole:"खड्डा",road:"रस्त्याचे नुकसान",light:"स्ट्रीट लाईट",water:"पाणी साचणे"}
};
const fallback={en:T.en,hi:T.hi,mr:T.mr};
let lang=localStorage.getItem("cs-lang")||"en";
function tr(key){return (T[lang]||T.en)[key]||(T.en[key]||key)}
function applyLang(){
 document.querySelectorAll("[data-t]").forEach(e=>e.textContent=tr(e.dataset.t));
 document.documentElement.lang=lang; localStorage.setItem("cs-lang",lang);
 const s=document.getElementById("language"); if(s)s.value=lang;
}
function theme(){
 document.body.classList.toggle("dark",localStorage.getItem("cs-theme")==="dark");
 const b=document.getElementById("theme"); if(b)b.textContent=document.body.classList.contains("dark")?"☀":"☾";
}
function toast(x){const e=document.getElementById("toast");if(!e)return;e.textContent=x;e.classList.add("show");setTimeout(()=>e.classList.remove("show"),2400)}
document.addEventListener("DOMContentLoaded",()=>{
 theme();applyLang();
 document.getElementById("theme")?.addEventListener("click",()=>{localStorage.setItem("cs-theme",document.body.classList.contains("dark")?"light":"dark");theme()});
 document.getElementById("language")?.addEventListener("change",e=>{lang=e.target.value;applyLang()});
});
