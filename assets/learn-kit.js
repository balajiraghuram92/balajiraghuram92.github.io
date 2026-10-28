/* Learn kit: pseudo code + imports + "View code" toggle, and MCQ quizzes.
   See learn-kit.css. Markup contract:

   <div class="lk-code">
     <div class="lk-pseudo"><div class="lk-label">Pseudo code</div><pre>...</pre></div>
     <div class="lk-imports"><div class="lk-label">Imported</div><ul><li>...</li></ul></div>
     <details class="lk-reveal"><summary>View code</summary> original code block </details>
   </div>

   <div class="lk-quiz">
     <h4 class="lk-quiz-title">Check your understanding</h4>
     <div class="lk-q">
       <p class="lk-stem">Question?</p>
       <ol class="lk-opts">
         <li>Option text<div class="lk-why">Why this option is wrong.</div></li>
         <li data-correct>Option text<div class="lk-why">Why this option is right.</div></li>
       </ol>
     </div>
   </div>
*/
(function(){
  "use strict";
  var KW=/\b(SET|LET|IF|ELSE IF|ELSE|THEN|END IF|FOR EACH|FOR|IN|WHILE|REPEAT|UNTIL|END FOR|END WHILE|DEFINE|FUNCTION|CLASS|RETURN|CALL|PRINT|SHOW|READ|LOAD|IMPORT|CREATE|BUILD|SEND|ASK|WAIT|TRY|CATCH|WITH|ON ERROR|RUN|START|STOP|STORE|SAVE|APPEND|ADD|UPDATE|DELETE|AND|OR|NOT|OTHERWISE|INPUT|OUTPUT|END)\b/g;

  function esc(s){return s.replace(/[&<>]/g,function(c){return c==="&"?"&amp;":c==="<"?"&lt;":"&gt;";});}

  function initPseudo(root){
    root.querySelectorAll(".lk-pseudo pre:not([data-lk])").forEach(function(pre){
      pre.setAttribute("data-lk","1");
      var lines=pre.textContent.replace(/^\n+|\s+$/g,"").split("\n");
      pre.innerHTML=lines.map(function(line){
        // a comment is "//" at line start or after whitespace, so URLs like https:// stay intact
        var m=/(^|\s)\/\//.exec(line),code=line,cm="";
        if(m){var i=m.index+m[1].length;code=line.slice(0,i);cm=line.slice(i);}
        return esc(code).replace(KW,'<b class="lk-kw">$1</b>')+(cm?'<span class="lk-cm">'+esc(cm)+"</span>":"");
      }).join("\n");
    });
  }

  function initReveal(root){
    root.querySelectorAll("details.lk-reveal>summary:not([data-lk])").forEach(function(s){
      s.setAttribute("data-lk","1");
      if(!s.querySelector(".lk-show")){
        var label=s.textContent.trim()||"View code";
        s.innerHTML='<span class="lk-show">'+esc(label)+'</span><span class="lk-hide">Hide code</span>';
      }
    });
  }

  function initQuiz(root){
    root.querySelectorAll(".lk-quiz:not([data-lk])").forEach(function(quiz){
      quiz.setAttribute("data-lk","1");
      var qs=[].slice.call(quiz.querySelectorAll(".lk-q"));
      var score=document.createElement("p");score.className="lk-score";
      var reset=document.createElement("button");reset.type="button";reset.className="lk-reset";reset.textContent="Try again";
      var answered=0,right=0;
      function update(){
        score.textContent="Score: "+right+" of "+qs.length+(answered<qs.length?" ("+answered+" answered)":right===qs.length?". All correct!":". Review the explanations above, then try again.");
      }
      qs.forEach(function(q,qi){
        var items=[].slice.call(q.querySelectorAll(".lk-opts>li"));
        var correct=items.findIndex(function(li){return li.hasAttribute("data-correct");});
        var fb=document.createElement("div");fb.className="lk-feedback";fb.setAttribute("aria-live","polite");
        var data=items.map(function(li,oi){
          var w=li.querySelector(".lk-why"),why=w?w.innerHTML:"";
          if(w)w.remove();
          var text=li.innerHTML.trim();
          var b=document.createElement("button");b.type="button";b.className="lk-opt";
          var letter=String.fromCharCode(65+oi);
          b.innerHTML='<span class="lk-letter">'+letter+'.</span><span>'+text+"</span>";
          li.innerHTML="";li.appendChild(b);
          b.addEventListener("click",function(){
            if(q.classList.contains("lk-answered"))return;
            q.classList.add("lk-answered");answered++;
            items.forEach(function(x){x.firstChild.disabled=true;});
            var c=data[correct];
            if(oi===correct){
              right++;b.classList.add("lk-right");
              fb.innerHTML='<p><span class="lk-ok">Correct.</span> '+why+"</p>";
            }else{
              b.classList.add("lk-wrong");c.btn.classList.add("lk-right");
              fb.innerHTML='<p><span class="lk-no">Not quite.</span> You picked <b>'+letter+".</b> "+why+"</p>"+
                '<p><span class="lk-ok">The correct answer is '+c.letter+":</span> <b>"+c.text+"</b></p>"+
                "<p>"+c.why+"</p>";
            }
            update();
          });
          return {btn:b,letter:letter,text:text,why:why};
        });
        q.appendChild(fb);
        q._lkReset=function(){q.classList.remove("lk-answered");fb.innerHTML="";data.forEach(function(d){d.btn.disabled=false;d.btn.classList.remove("lk-right","lk-wrong");});};
      });
      reset.addEventListener("click",function(){answered=0;right=0;qs.forEach(function(q){q._lkReset();});update();});
      quiz.appendChild(score);quiz.appendChild(reset);update();
    });
  }

  function init(root){root=root||document;initPseudo(root);initReveal(root);initQuiz(root);}

  // printing: show every hidden code block
  addEventListener("beforeprint",function(){document.querySelectorAll("details.lk-reveal:not([open])").forEach(function(d){d.setAttribute("open","");d.setAttribute("data-lk-print","");});});
  addEventListener("afterprint",function(){document.querySelectorAll("details.lk-reveal[data-lk-print]").forEach(function(d){d.removeAttribute("open");d.removeAttribute("data-lk-print");});});

  window.LearnKit={init:init};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){init();});else init();
})();
