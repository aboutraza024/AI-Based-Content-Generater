// CWT Application State
const state = {
    region: 'USA English',
    contentType: 'informational',
    productName: '',
    targetAudience: 'General Audience',
    tone: 'professional',
    sense: '',
    wordCount: 800,

    outlineResponse: null,
    confirmedOutline: '',
    generateResponse: null
};

// Helper to escape HTML characters safely
function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Markdown to HTML Parser for VIP Article Rendering
function parseMarkdownToVIPHtml(markdownText) {
    if (!markdownText) return '';

    let html = markdownText;

    // Convert Headers
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');

    // Convert Bold & Italic
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

    // Convert Bullet Lists
    html = html.replace(/^\- (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gim, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/gim, '');

    // Convert Paragraphs
    const lines = html.split('\n');
    const processedLines = lines.map(line => {
        line = line.trim();
        if (line.startsWith('<h') || line.startsWith('<ul') || line.startsWith('<li') || line.startsWith('</ul') || line === '') {
            return line;
        }
        return `<p>${line}</p>`;
    });

    return processedLines.join('\n');
}

// Competitor Analysis Summary Markdown Parser for Executive Dashboard
function parseFormattedCompetitorSummary(rawText) {
    if (!rawText) return '';
    let html = rawText;

    // Convert Bold text
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');

    // Convert Section Subheadings (e.g. - **Topics/angles competitors are covering**)
    html = html.replace(/^[-\*]\s*<strong>(.*?)<\/strong>/gim, '<div style="font-weight:700; color:#2563eb; margin-top:10px; font-size:13px;">📌 $1</div>');

    // Convert Bullets
    html = html.replace(/^[-\*]\s*(.*$)/gim, '<li style="margin-left:14px; margin-bottom:4px;">$1</li>');
    html = html.replace(/(<li.*<\/li>)/gim, '<ul style="padding-left:10px; margin-top:4px; margin-bottom:8px;">$1</ul>');
    html = html.replace(/<\/ul>\s*<ul.*?>/gim, '');

    return html;
}

// Show/Hide State Cards
function showState(cardId) {
    ['empty-state', 'loading-state', 'outline-approval-card', 'article-output-card'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            if (id === cardId) {
                el.style.display = 'block';
            } else if (id === 'article-output-card' && cardId === 'article-output-card') {
                el.style.display = 'block';
            } else if (id !== 'article-output-card') {
                el.style.display = 'none';
            }
        }
    });
}

// Helper to show/hide Error Banner
function showErrorBanner(msg) {
    const banner = document.getElementById('error-banner');
    const msgEl = document.getElementById('error-banner-msg');
    if (banner && msgEl) {
        msgEl.textContent = msg;
        banner.style.display = 'block';
    }
}

function hideErrorBanner() {
    const banner = document.getElementById('error-banner');
    if (banner) banner.style.display = 'none';
}

// 1. Submit Form Parameters & Generate Outline
async function handleOutlineSubmit(e) {
    if (e) {
        e.preventDefault();
        if (e.stopPropagation) e.stopPropagation();
    }

    hideErrorBanner();

    const btn = document.getElementById('btn-generate-outline');
    
    try {
        state.region = document.getElementById('input-region').value;
        state.contentType = document.getElementById('input-type').value;
        state.productName = document.getElementById('input-product').value.trim();
        const audEl = document.getElementById('input-audience');
        state.targetAudience = audEl ? (audEl.value.trim() || "General Audience") : "General Audience";
        state.tone = document.getElementById('input-tone').value;
        state.wordCount = parseInt(document.getElementById('input-wordcount').value);
        const senseEl = document.getElementById('input-sense');
        state.sense = senseEl ? (senseEl.value.trim() || "High quality comprehensive coverage") : "High quality comprehensive coverage";

        if (!state.productName) {
            showErrorBanner("Please enter a Product / Article Topic Name before generating.");
            return;
        }

        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '⏳ Analyzing Competitors...';
        }

        // Hide Article output if previous run
        document.getElementById('article-output-card').style.display = 'none';
        document.getElementById('feedback-input-box').style.display = 'none';

        // Show Loading
        const startTime = Date.now();
        showState('loading-state');
        document.getElementById('loading-title').textContent = "Analyzing Competitors & Structuring Outline...";
        document.getElementById('loading-sub').textContent = "Executing parallel Tavily web search graph & Azure OpenAI gpt-5.4 model...";

        const response = await fetch('/api/v1/outline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                language: "English",
                region: state.region,
                content_type: state.contentType,
                product_name: state.productName,
                target_audience: state.targetAudience,
                tone: state.tone,
                sense: state.sense,
                word_count: state.wordCount,
                include_meta: true
            })
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Server returned HTTP ${response.status}`);
        }

        const data = await response.json();
        state.outlineResponse = data;
        const latencySec = ((Date.now() - startTime) / 1000).toFixed(1);

        // Render Executive Competitor Dashboard
        const comp = data.competitor_analysis || {};
        const compBody = document.getElementById('comp-summary-body');
        const formattedSummary = parseFormattedCompetitorSummary(comp.summary || "");

        const topicsList = (comp.topics_covered || []).map(t => `<li>${escapeHtml(t)}</li>`).join('');

        compBody.innerHTML = `
            <div class="comp-exec-header">
                <span class="comp-query-pill">🔍 Search: "${escapeHtml(data.query_used)}"</span>
                <div>
                    <span class="badge-blue">⚡ Execution: ${latencySec}s</span>
                    <span class="badge-green" style="margin-left:6px;">✓ Deep Competitor Coverage</span>
                </div>
            </div>

            <div class="comp-grid-cards">
                <div class="comp-card-item">
                    <div class="comp-card-title">📌 Topics & Angles Covered</div>
                    <div class="comp-card-body">
                        <ul>${topicsList}</ul>
                    </div>
                </div>

                <div class="comp-card-item style-card">
                    <div class="comp-card-title">✍️ Format & Writing Style</div>
                    <div class="comp-card-body">
                        <div><strong>Structure:</strong> ${escapeHtml(comp.style_structure || "")}</div>
                        <div class="mt-1"><strong>Depth:</strong> ${escapeHtml(comp.depth_scope || "")}</div>
                    </div>
                </div>
            </div>

            <div class="comp-card-item gap-card mt-3">
                <div class="comp-card-title">💡 Strategic Analysis & Opportunity Gaps</div>
                <div class="comp-card-body">
                    ${formattedSummary}
                </div>
            </div>
        `;

        // Render Formatted Outline Preview
        const formattedOutlineHtml = parseMarkdownToVIPHtml(data.outline);
        document.getElementById('outline-formatted-view').innerHTML = formattedOutlineHtml;
        document.getElementById('outline-raw-editor').value = data.outline;

        showState('outline-approval-card');

    } catch (err) {
        showErrorBanner(`API Error: ${err.message}`);
        showState('empty-state');
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '🔍 Analyze Competitors & Create Outline';
        }
    }
}

// Toggle Raw Markdown Editor
function toggleOutlineEditor() {
    const rawEditor = document.getElementById('outline-raw-editor');
    const formattedView = document.getElementById('outline-formatted-view');
    if (rawEditor.style.display === 'none') {
        rawEditor.style.display = 'block';
        formattedView.style.display = 'none';
    } else {
        rawEditor.style.display = 'none';
        formattedView.style.display = 'block';
        formattedView.innerHTML = parseMarkdownToVIPHtml(rawEditor.value);
    }
}

// 2. Button "No, I Want Changes" -> Show Feedback Box
function showFeedbackInput() {
    const box = document.getElementById('feedback-input-box');
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
}

// Submit Custom Feedback Changes for Outline
async function recreateOutlineWithFeedback() {
    const feedback = document.getElementById('outline-feedback-text').value.trim();
    if (!feedback) {
        alert("Please type your custom changes.");
        return;
    }

    state.sense += ` | User Outline Feedback: ${feedback}`;
    handleOutlineSubmit(null);
}

// 3. Button "Yes, Accept & Generate Article" -> Full Content Generation
async function approveOutlineAndGenerate() {
    const rawEditor = document.getElementById('outline-raw-editor');
    const outlineText = (rawEditor && rawEditor.value.trim()) ? rawEditor.value.trim() : state.outlineResponse.outline;

    state.confirmedOutline = outlineText;

    // Show Loading
    const startTime = Date.now();
    showState('loading-state');
    document.getElementById('loading-title').textContent = "Crafting VIP Humanized Article...";
    document.getElementById('loading-sub').textContent = "Running parallel Humanization rewrite chain & Mechanical Linter Audit...";

    try {
        const response = await fetch('/api/v1/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                language: "English",
                region: state.region,
                content_type: state.contentType,
                product_name: state.productName,
                target_audience: state.targetAudience,
                tone: state.tone,
                sense: state.sense,
                word_count: state.wordCount,
                confirmed_outline: state.confirmedOutline,
                competitor_summary: state.outlineResponse ? state.outlineResponse.competitor_analysis.summary : '',
                include_meta: true
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Full article generation failed.");
        }

        const data = await response.json();
        state.generateResponse = data;
        const latencySec = ((Date.now() - startTime) / 1000).toFixed(1);

        // Hide Loading and Keep Outline Card Visible + Show Article Card
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('outline-approval-card').style.display = 'block';

        renderVIPArticleOutput(data, latencySec);

    } catch (err) {
        alert(`Error: ${err.message}`);
        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('outline-approval-card').style.display = 'block';
    }
}

// Render VIP Article Output
function renderVIPArticleOutput(data, latencySec = null) {
    const articleCard = document.getElementById('article-output-card');
    articleCard.style.display = 'block';

    document.getElementById('article-main-heading').textContent = state.productName;
    const speedBadge = latencySec ? ` | ⚡ Speed: ${latencySec}s` : '';
    document.getElementById('article-wc-badge').textContent = `Words: ${data.word_count_actual}${speedBadge}`;

    // Linter Metrics Pills
    const r = data.lint_report;
    const metricsContainer = document.getElementById('linter-metrics-container');
    metricsContainer.innerHTML = `
        <span class="audit-metric-pill">✓ Semicolons Removed: ${r.semicolons_removed}</span>
        <span class="audit-metric-pill">✓ Oxford Commas Stripped: ${r.oxford_commas_removed}</span>
        <span class="audit-metric-pill">✓ Dashes Fixed: ${r.hyphens_removed}</span>
        <span class="audit-metric-pill">✓ Sentence Starts Varied: ${r.repetitive_starts_fixed}</span>
    `;

    // Format & Render Prose Body
    const vipHtml = parseMarkdownToVIPHtml(data.final_content);
    document.getElementById('article-prose-body').innerHTML = vipHtml;

    // Meta Description & Tags
    if (data.meta_description) {
        document.getElementById('article-meta-desc').textContent = data.meta_description;
        const tagsFlex = document.getElementById('article-meta-tags');
        tagsFlex.innerHTML = '';
        (data.meta_tags || []).forEach(t => {
            const span = document.createElement('span');
            span.className = 'tag-badge';
            span.textContent = t;
            tagsFlex.appendChild(span);
        });
    }

    articleCard.scrollIntoView({ behavior: 'smooth' });
}

// Copy Article Content
function copyArticleContent() {
    const text = document.getElementById('article-prose-body').innerText;
    navigator.clipboard.writeText(text).then(() => {
        alert("VIP Formatted Article copied to clipboard!");
    });
}

// Submit Article for Humanization (replaces old revision endpoint)
async function submitArticleRevision() {
    const instructions = document.getElementById('article-revision-input').value.trim();

    showState('loading-state');
    document.getElementById('loading-title').textContent = "Humanizing Article...";
    document.getElementById('loading-sub').textContent = "Running senior editorial humanization pass...";

    // Fold any optional instructions the user typed into the text sent for
    // humanization, since the /humanize endpoint only accepts raw text.
    const textToHumanize = instructions
        ? `${state.generateResponse.final_content}\n\n[Additional instructions: ${instructions}]`
        : state.generateResponse.final_content;

    try {
        const response = await fetch('/api/v1/humanize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content_type: state.contentType,
                target_audience: state.targetAudience,
                tone: state.tone,
                text: textToHumanize
            })
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.detail || "Article humanization failed.");
        }

        const data = await response.json();
        state.generateResponse.final_content = data.humanized_content;
        state.generateResponse.word_count_actual = data.word_count_actual;

        document.getElementById('loading-state').style.display = 'none';
        document.getElementById('outline-approval-card').style.display = 'block';

        renderVIPArticleOutput(state.generateResponse);

    } catch (err) {
        alert(`Error: ${err.message}`);
        document.getElementById('loading-state').style.display = 'none';
    }
}

// Start New Project
function startNewProject() {
    document.getElementById('setup-form').reset();
    showState('empty-state');
    document.getElementById('article-output-card').style.display = 'none';
}
