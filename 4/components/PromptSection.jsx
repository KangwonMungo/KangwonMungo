import React from "react";

export default function PromptSection() {
  return (
    <section className="prompt-section">
      <div className="user-message">
        응. 판타지 장르, 주인공이 성장하는 내용을 좋아하고, 세계관이 독특해야해! 이런 책 있으면 알려줄래?
      </div>
      <div className="ai-recommend">
        혹시 다음과 같은 책들은 어떠신가요?
        <ul>
          <li>
            <b>《황금나침반 (His Dark Materials 시리즈 1)》 - 필립 풀먼</b><br />
            요약: 평행 세계를 배경으로 소녀 라라가 진실을 찾아 모험하며 성장하는 이야기.<br />
            추천 이유: 독특한 세계관과 매력적인 주인공의 성장, 깊이 있는 주제가 흥미를 끕니다.
          </li>
          <li>
            <b>《안개born 1: 마지막 제국》 - 브랜든 샌더슨</b><br />
            요약: 독특한 능력과 어두운 세계 속에서 도둑 소녀 빈이 혁명의 불씨를 피우며 성장하는 이야기.<br />
            추천 이유: 참신한 능력 설정과 예측 불가능한 스토리, 강렬한 주인공의 성장이 인상적
          </li>
        </ul>
      </div>
    </section>
  );
} 