/**
 * Pure Client-side Bijoy (ANSI / SutonnyMJ) to Unicode Converter.
 * 100% Offline, runs directly in browser/webview without any backend server.
 */

window.BijoyToUnicode = (function () {
  'use strict';

  const preConversionMap = {
    ' +': ' ',
    'yy': 'y',
    'vv': 'v',
    'y&': 'y',
    '„&': '„',
    '‡u': 'u‡',
    'wu': 'uw',
    ' ,': ',',
    ' \\|': '\\|',
    '\\\\ ': '',
    ' \\\\': '',
    '\\\\': '',
    '\n +': '\n',
    ' +\n': '\n',
  };

  const conversionMap = {
    // Multi-character overrides
    'šÍ': 'ন্ত',
    'š’': 'ন্থ',
    'š‘': 'ন্তু',
    'Av': 'আ',
    'A': 'অ',
    'B': 'ই',
    'C': 'ঈ',
    'D': 'উ',
    'E': 'ঊ',
    'F': 'ঋ',
    'G': 'এ',
    'H': 'ঐ',
    'I': 'ও',
    'J': 'ঔ',
    'K': 'ক',
    'L': 'খ',
    'M': 'গ',
    'N': 'ঘ',
    'O': 'ঙ',
    'P': 'চ',
    'Q': 'ছ',
    'R': 'জ',
    'S': 'ঝ',
    'T': 'ঞ',
    'U': 'ট',
    'V': 'ঠ',
    'W': 'ড',
    'X': 'ঢ',
    'Y': 'ণ',
    'Z': 'ত',
    '_': 'থ',
    '`': 'দ',
    'a': 'ধ',
    'b': 'ন',
    'c': 'প',
    'd': 'ফ',
    'e': 'ব',
    'f': 'ভ',
    'g': 'ম',
    'h': 'য',
    'i': 'র',
    'j': 'ল',
    'k': 'শ',
    'l': 'ষ',
    'm': 'স',
    'n': 'হ',
    'o': 'ড়',
    'p': 'ঢ়',
    'q': 'য়',
    'r': 'ৎ',
    's': 'ং',
    't': 'ঃ',
    'u': 'ঁ',
    '0': '০',
    '1': '১',
    '2': '২',
    '3': '৩',
    '4': '৪',
    '5': '৫',
    '6': '৬',
    '7': '৭',
    '8': '৮',
    '9': '৯',
    '•': 'ঙ্',
    'v': 'া',
    'w': 'ি',
    'x': 'ী',
    'y': 'ু',
    'z': 'ু',
    '“': 'ু',
    '–': 'ু',
    '~': 'ূ',
    'ƒ': 'ূ',
    '‚': 'ূ',
    '„„': 'ৃ',
    '„': 'ৃ',
    '…': 'ৃ',
    '†': 'ে',
    '‡': 'ে',
    'ˆ': 'ৈ',
    '‰': 'ৈ',
    'Š': 'ৗ',
    '\\|': '।',
    '|': '।',
    '\\&': '্‌',
    '&': '্',
    '\\^': '্ব',
    '^': '্ব',
    'ÿ': 'ক্ষ',
    '‘': '্তু',
    '’': '্থ',
    '‹': '্ক',
    'Œ': '্ক্র',
    '”': 'চ্',
    '—': '্ত',
    '˜': 'দ্',
    '™': 'দ্',
    'š': 'ন্',
    '›': 'ন্',
    'œ': '্ন',
    'Ÿ': '্ব',
    '¡': '্ব',
    '¢': '্ভ',
    '£': '্ভ্র',
    '¤': 'ম্',
    '¥': '্ম',
    '¦': '্ব',
    '§': '্ম',
    '¨': '্য',
    '©': 'র্',
    'ª': '্র',
    '«': '্র',
    '¬': '্ল',
    '­': '্ল',
    '®': 'ষ্',
    '¯': 'স্',
    '°': 'ক্ক',
    '±': 'ক্ট',
    '²': 'ক্ষ্ণ',
    '³': 'ক্ত',
    '´': 'ক্ম',
    'µ': 'ক্র',
    '¶': 'ক্ষ',
    '·': 'ক্স',
    '¸': 'গু',
    '¹': 'জ্ঞ',
    'º': 'গ্দ',
    '»': 'গ্ধ',
    '¼': 'ঙ্ক',
    '½': 'ঙ্গ',
    '¾': 'জ্জ',
    '¿': '্ত্র',
    'À': 'জ্ঝ',
    'Á': 'জ্ঞ',
    'Â': 'ঞ্চ',
    'Ã': 'ঞ্ছ',
    'Ä': 'ঞ্জ',
    'Å': 'ঞ্ঝ',
    'Æ': 'ট্ট',
    'Ç': 'ড্ড',
    'È': 'ণ্ট',
    'É': 'ণ্ঠ',
    'Ê': 'ণ্ড',
    'Ë': 'ত্ত',
    'Ì': 'ত্থ',
    'Í': 'ত্ম',
    'Î': 'ত্র',
    'Ï': 'দ্দ',
    'Ð': '-',
    'Ñ': '-',
    'Ò': '"',
    'Ó': '"',
    'Ô': "'",
    'Õ': "'",
    'Ö': '্র',
    '×': 'দ্ধ',
    'Ø': 'দ্ব',
    'Ù': 'দ্ম',
    'Ú': 'ন্ঠ',
    'Û': 'ন্ড',
    'Ü': 'ন্ধ',
    'Ý': 'ন্স',
    'Þ': 'প্ট',
    'ß': 'প্ত',
    'à': 'প্প',
    'á': 'প্স',
    'â': 'ব্জ',
    'ã': 'ব্দ',
    'ä': 'ব্ধ',
    'å': 'ভ্র',
    'æ': 'ম্ন',
    'ç': 'ম্ফ',
    'è': '্ন',
    'é': 'ল্ক',
    'ê': 'ল্গ',
    'ë': 'ল্ট',
    'ì': 'ল্ড',
    'í': 'ল্প',
    'î': 'ল্ফ',
    'ï': 'শু',
    'ð': 'শ্চ',
    'ñ': 'শ্ছ',
    'ò': 'ষ্ণ',
    'ó': 'ষ্ট',
    'ô': 'ষ্ঠ',
    'õ': 'ষ্ফ',
    'ö': 'স্খ',
    '÷': 'স্ট',
    'ø': 'স্ন',
    'ù': 'স্ফ',
    'ú': '্প',
    'û': 'হু',
    'ü': 'হৃ',
    'ý': 'হ্ন',
    'þ': 'হ্ম',
  };

  const postConversionMap = {
    '০ঃ': '০:',
    '১ঃ': '১:',
    '২ঃ': '২:',
    '৩ঃ': '৩:',
    '৪ঃ': '৪:',
    '৫ঃ': '৫:',
    '৬ঃ': '৬:',
    '৭ঃ': '৭:',
    '৮ঃ': '৮:',
    '৯ঃ': '৯:',
    ' ঃ': ':',
    '\nঃ': '\n:',
    ']ঃ': ']:',
    '  ': ' ',
    'অা': 'আ',
    '্‌্‌': '্‌',
    '্্': '্',
  };

  const preKars = new Set(['ি', 'ৈ', 'ে']);
  const postKars = new Set(['া', 'ো', 'ৌ', 'ৗ', 'ু', 'ূ', 'ী', 'ৃ']);
  const consonants = new Set([
    'ক', 'খ', 'গ', 'ঘ', 'ঙ', 'চ', 'ছ', 'জ', 'ঝ', 'ঞ',
    'ট', 'ঠ', 'ড', 'ঢ', 'ণ', 'ত', 'থ', 'দ', 'ধ', 'ন',
    'প', 'ফ', 'ব', 'ভ', 'ম', 'য', 'র', 'ল', 'শ', 'ষ',
    'স', 'হ', 'ড়', 'ঢ়', 'য়', 'ৎ', 'ং', 'ঃ', 'ঁ'
  ]);

  function safeChar(str, idx) {
    return (idx >= 0 && idx < str.length) ? str[idx] : '';
  }

  function rearrangeUnicode(str) {
    let s = str;
    let i = 0;
    while (i < s.length) {
      // 1. Ref (র + ্) reordering
      if (i < s.length - 1 && safeChar(s, i) === 'র' && safeChar(s, i + 1) === '্' && safeChar(s, i - 1) !== '্') {
        let j = 1;
        while (true) {
          const prev = safeChar(s, i - j);
          const prevPrev = safeChar(s, i - j - 1);
          if (i - j < 0) break;
          if (consonants.has(prev) && prevPrev === '্') {
            j += 2;
          } else if (j === 1 && (preKars.has(prev) || postKars.has(prev))) {
            j += 1;
          } else {
            break;
          }
        }
        const start = Math.max(0, i - j);
        s = s.substring(0, start) + s.substring(i, i + 2) + s.substring(start, i) + s.substring(i + 2);
        i += 1;
        continue;
      }

      // 2. Vowel + Halant + Consonant -> Halant + Consonant + Vowel
      if (i > 0 && safeChar(s, i) === '্' && (preKars.has(safeChar(s, i - 1)) || postKars.has(safeChar(s, i - 1))) && i < s.length - 1) {
        s = s.substring(0, i - 1) + s.substring(i, i + 2) + safeChar(s, i - 1) + s.substring(i + 2);
      }

      // 3. Pre-kar (ি, ে, ৈ) reordering
      if (i < s.length - 1 && preKars.has(safeChar(s, i)) && !/\s/.test(safeChar(s, i + 1))) {
        let j = 1;
        while (i + j < s.length && consonants.has(safeChar(s, i + j))) {
          if (i + j + 1 < s.length && safeChar(s, i + j + 1) === '্') {
            j += 2;
          } else {
            break;
          }
        }

        let temp = s.substring(0, i) + s.substring(i + 1, i + j + 1);
        let l = 0;
        const currKar = safeChar(s, i);
        const nextKar = safeChar(s, i + j + 1);

        if (currKar === 'ে' && nextKar === 'া') {
          temp += 'ো';
          l = 1;
        } else if (currKar === 'ে' && nextKar === 'ৗ') {
          temp += 'ৌ';
          l = 1;
        } else {
          temp += currKar;
        }

        temp += s.substring(i + j + l + 1);
        s = temp;
        i += j;
      }

      i += 1;
    }
    return s;
  }

  function convert(text) {
    if (!text) return '';

    // Protect (cid:X) from being converted using Unicode PUA characters
    const cidPlaceholders = [];
    text = text.replace(/\(?cid:\d+\)?/gi, (match) => {
      const idx = cidPlaceholders.length;
      cidPlaceholders.push(match);
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      return '\uE000' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE001';
    });

    // Apply pre-conversion regex
    for (const [pattern, rep] of Object.entries(preConversionMap)) {
      text = text.replace(new RegExp(pattern, 'g'), rep);
    }

    // Sort conversion keys by length descending
    const keys = Object.keys(conversionMap).sort((a, b) => b.length - a.length);
    const result = [];
    let i = 0;
    const n = text.length;

    while (i < n) {
      let matched = false;
      for (const k of keys) {
        if (text.startsWith(k, i)) {
          result.push(conversionMap[k]);
          i += k.length;
          matched = true;
          break;
        }
      }
      if (!matched) {
        result.push(text[i]);
        i += 1;
      }
    }

    let intermediate = result.join('');
    let rearranged = rearrangeUnicode(intermediate);

    for (const [pattern, rep] of Object.entries(postConversionMap)) {
      rearranged = rearranged.split(pattern).join(rep);
    }

    // Restore cid tokens
    for (let idx = 0; idx < cidPlaceholders.length; idx++) {
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      const placeholder = '\uE000' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE001';
      rearranged = rearranged.split(placeholder).join(cidPlaceholders[idx]);
    }

    return rearranged;
  }

  const BIJOY_SPECIALS = /[†‡ˆ‰Š‹Œ”˜™š›œŸ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþ]/;

  const BIJOY_EXACT_WORDS = new Set([
    'eivei', 'cwiPvjK', 'gnvcwiPvjK', 'miKvi', 'wefvM', 'Dc‡Rjv', 'Zvs', 'wkÿv',
    'cixÿv', '†Pqvig¨vb', 'mnKvix', 'MYcÖRvZš¿x', 'Av‡e', 'evsjv', 'evsjvq', 'evsjvi',
    'Avgvi', 'Avwg', 'Avgv‡`i', 'Avgv‡K', 'Avgvq', 'Avcbvi', 'Avcbv‡`i', 'Mvb', 'MvB',
    '†mvbvi', '†Zvgvq', 'cÖ_g', 'wØZxq', 'ZvwiL', 'weeiY', 'mKj', 'Rb¨', 'hy³', 'wPÎ',
    'wbe©vPb', 'gvÎ', 'c„ôv', 'gš¿Yvjq', 'Awa', 'Awdm', 'AvBb', 'evsjv‡`k', 'evsjv‡`kx',
    'fvj', 'fv‡jv', 'K‡i', 'n‡e', 'GB', '†h', '†m', 'bv', 'hveZxq', 'mshy³',
    '¯^vÿi', 'Abywjwc', 'wmw×', 'MwVZ', 'nIqv', 'wewfbœ', 'we‡kl', 'welq', 'Dci',
    'AvaywbK', 'cÖKvk', 'msNwVZ', 'mswkøó', 'cÖavb', 'weMZ', 'cÖ`vb', 'Av‡e`b',
    'Av‡jvPbv', 'Dcgnv', 'wb‡qvM', 'weÁwß', 'cÎ', 'wek^vm', 'wk^vm', 'cÖwZ',
    'ZvB', 'fvB', 'hw`', 'wKš‘', 'KviY', 'Ges', 'A_ev', 'ev', 'wQj', 'Av‡Q', '†bB'
  ]);

  const BIJOY_CONSONANT_KARS = /([K-Z][vwxy])|([jckdfgpq]v)|(vq)|(xq)|(sj)|(w[K-Z])|(\bw[kmpbftdcjqzly])|(&[K-Za-z])|(\bAv[a-zA-Z])/;

  const ENGLISH_COMMON = new Set([
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
    'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
    'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
    'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
    'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
    'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work',
    'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these',
    'give', 'day', 'most', 'us', 'is', 'are', 'was', 'were', 'been', 'has',
    'had', 'report', 'project', 'table', 'date', 'name', 'title', 'status',
    'director', 'general', 'executive', 'officer', 'department', 'ministry',
    'government', 'page', 'code', 'file', 'data', 'test', 'result', 'error',
    'warning', 'success', 'hello', 'world', 'summary', 'details', 'total'
  ]);

  function isBijoyToken(token) {
    if (!token) return false;
    const clean = token.replace(/^[.,;:?!'"()\[\]{}<>«»\u201c\u201d\u2018\u2019/\\|\-*#_~0-9]+|[.,;:?!'"()\[\]{}<>«»\u201c\u201d\u2018\u2019/\\|\-*#_~0-9]+$/g, '');
    if (!clean) return false;
    if (/[\u0980-\u09FF]/.test(clean)) return false;
    if (BIJOY_SPECIALS.test(clean)) return true;
    if (ENGLISH_COMMON.has(clean.toLowerCase())) return false;
    if (BIJOY_EXACT_WORDS.has(clean)) return true;
    if (BIJOY_CONSONANT_KARS.test(clean)) return true;
    return false;
  }

  function isLikelyBijoy(text) {
    if (!text) return false;
    if (BIJOY_SPECIALS.test(text)) return true;

    // If text already contains modern Unicode Bengali (> 15 chars) and no Bijoy specials, do not alter it
    const unicodeMatches = text.match(/[\u0980-\u09FF]/g);
    if (unicodeMatches && unicodeMatches.length >= 15) {
      return false;
    }

    const markers = ['Avgvi', 'evsjv', 'wPÎ', 'cÖ', 'hy³', 'Avwg', '†mvbvi', '†Zvgvq', 'eivei', 'cwiPvjK', 'miKvi'];
    for (const m of markers) {
      if (text.includes(m)) return true;
    }
    const tokens = text.split(/\s+/).slice(0, 80);
    const count = tokens.filter(isBijoyToken).length;
    return count >= 2;
  }

  function convertMarkdown(markdownText) {
    if (!markdownText || !isLikelyBijoy(markdownText)) return markdownText;

    // 0. Protect Math blocks
    const mathBlocks = [];
    let text = markdownText.replace(/\$\$[\s\S]*?\$\$/g, m => {
      mathBlocks.push(m);
      return `__MATH_BLOCK_${mathBlocks.length - 1}__`;
    });

    const inlineMaths = [];
    text = text.replace(/\$[^\$\n]+?\$/g, m => {
      inlineMaths.push(m);
      return `__INLINE_MATH_${inlineMaths.length - 1}__`;
    });

    const codeBlocks = [];
    text = text.replace(/```[\s\S]*?```/g, m => {
      codeBlocks.push(m);
      return `__CODE_BLOCK_${codeBlocks.length - 1}__`;
    });

    const inlineCodes = [];
    text = text.replace(/`[^`\n]+`/g, m => {
      inlineCodes.push(m);
      return `__INLINE_CODE_${inlineCodes.length - 1}__`;
    });

    const urls = [];
    text = text.replace(/\[(.*?)\]\((https?:\/\/[^\s)]+|file:\/\/[^\s)]+|\/[^\s)]+)\)/g, (m, txt, url) => {
      urls.push(url);
      return `[${txt}](__URL_${urls.length - 1}__)`;
    });

    const lines = text.split('\n');
    const processed = [];

    for (const line of lines) {
      const stripped = line.trim();
      if (!stripped || stripped.startsWith('__CODE_BLOCK_')) {
        processed.push(line);
        continue;
      }

      const prefixMatch = line.match(/^(\s*(?:#{1,6}\s+|[-*+]\s+(?:\[[ xX]\]\s+)?|\d+\.\s+|>\s*))(.*)$/);
      const prefix = prefixMatch ? prefixMatch[1] : '';
      const content = prefixMatch ? prefixMatch[2] : line;

      if (stripped.startsWith('|') && stripped.endsWith('|')) {
        if (/^\|[\s:\-]+(?:\|[\s:\-]+)*\|$/.test(stripped)) {
          processed.push(line);
          continue;
        }
        const cells = content.split('|');
        const convertedCells = cells.map(cell => {
          const parts = cell.split(/(\s+|[.,;!?()[\]{}<>"'/\\:])/);
          return parts.map(p => isBijoyToken(p) ? convert(p) : p).join('');
        });
        processed.push(prefix + convertedCells.join('|'));
        continue;
      }

      const tokens = content.match(/\S+/g) || [];
      const hasBijoy = tokens.some(isBijoyToken);
      if (!hasBijoy) {
        processed.push(line);
        continue;
      }

      const parts = content.split(/(\s+|[.,;!?()[\]{}<>"'/\\:])/);
      const convertedContent = parts.map(p => isBijoyToken(p) ? convert(p) : p).join('');
      processed.push(prefix + convertedContent);
    }

    let result = processed.join('\n');
    inlineMaths.forEach((im, idx) => { result = result.replace(`__INLINE_MATH_${idx}__`, im); });
    mathBlocks.forEach((mb, idx) => { result = result.replace(`__MATH_BLOCK_${idx}__`, mb); });
    urls.forEach((u, idx) => { result = result.replace(`__URL_${idx}__`, u); });
    inlineCodes.forEach((ic, idx) => { result = result.replace(`__INLINE_CODE_${idx}__`, ic); });
    codeBlocks.forEach((cb, idx) => { result = result.replace(`__CODE_BLOCK_${idx}__`, cb); });

    return result;
  }

  // ==================== Unicode to Bijoy / ANSI Engine ====================
  const uToBConjuncts = [
    ['ক্ষ্ণ', '²'], ['স্ত্র', '¯¿'], ['ন্ত্ৰ', 'š¿'], ['ন্ত্র', 'š¿'], ['্ত্র', '¿'],
    ['র্চ্চ', '”P©'], ['র্চ্ছ', '”Q©'], ['স্প্ল', '¯cø'], ['স্ট্', '÷&'], ['স্ফ', 'ù'],
    ['স্ক', '¯‹'], ['স্ত', '¯Í'], ['স্থ', '¯’'], ['স্প', '¯ú'], ['স্ব', '¯^'],
    ['স্ন', '¯œ'], ['শ্র', 'kª'], ['শ্ল', 'kø'], ['শ্ব', 'k¦'], ['শ্ম', 'k¥'],
    ['শু', 'ï'], ['শ্চ', 'ð'], ['শ্ছ', 'ñ'], ['ষ্ণ', 'ò'], ['ষ্ট', 'ó'],
    ['ষ্ঠ', 'ô'], ['ষ্ফ', 'õ'], ['স্খ', 'ö'], ['স্ট', '÷'], ['হ্ন', 'ý'],
    ['হ্ম', 'þ'], ['হৃ', 'ü'], ['হু', 'û'], ['হ্ল', 'n¬'], ['ল্ক', 'é'],
    ['ল্গ', 'ê'], ['ল্ট', 'ë'], ['ল্ড', 'ì'], ['ল্প', 'í'], ['ল্ফ', 'î'],
    ['ল্ল', 'j&j'], ['ম্ন', 'æ'], ['ম্ফ', 'ç'], ['ম্ব', '¤^'], ['ম্ভ', '¤¢'],
    ['ম্ম', '¤§'], ['ব্জ', 'â'], ['ব্দ', 'ã'], ['ব্ধ', 'ä'], ['ব্ব', 'e&e'],
    ['ভ্র', 'å'], ['প্ট', 'Þ'], ['প্ত', 'ß'], ['প্প', 'à'], ['প্স', 'á'],
    ['প্ল', 'cø'], ['প্ন', 'cœ'], ['ন্ত', 'šÍ'], ['ন্থ', 'š’'], ['ন্তু', 'š‘'],
    ['ন্দ', '›'], ['ন্ধ', 'Ü'], ['ন্স', 'Ý'], ['ন্ন', 'bœ'], ['ন্ম', 'b¥'],
    ['ণ্ঠ', 'É'], ['ণ্ট', 'È'], ['ণ্ড', 'Ê'], ['ণ্ণ', 'Y&Y'], ['ত্ত', 'Ë'],
    ['ত্থ', 'Ì'], ['ত্ম', 'Í'], ['ত্র', 'Î'], ['দ্দ', 'Ï'], ['দ্ধ', '×'],
    ['দ্ব', 'Ø'], ['দ্ম', 'Ù'], ['ঞ্চ', 'Â'], ['ঞ্ছ', 'Ã'], ['ঞ্জ', 'Ä'],
    ['ঞ্ঝ', 'Å'], ['ট্ট', 'Æ'], ['ড্ড', 'Ç'], ['জ্ঞ', '¹'], ['গ্দ', 'º'],
    ['গ্ধ', '»'], ['ঙ্ক', '¼'], ['ঙ্গ', '½'], ['জ্জ', '¾'], ['জ্ঝ', 'À'],
    ['ক্ত', '³'], ['ক্ম', '´'], ['ক্র', 'µ'], ['ক্ষ', '¶'], ['ক্স', '·'],
    ['ক্ক', '°'], ['ক্ট', '±'], ['চ্ছ', '”Q'], ['চ্চ', '”P'], ['প্র', 'cÖ'],
    ['গ্র', 'MÖ']
  ];

  const uToBChars = {
    'অ': 'A', 'আ': 'Av', 'ই': 'B', 'ঈ': 'C', 'উ': 'D', 'ঊ': 'E', 'ঋ': 'F',
    'এ': 'G', 'ঐ': 'H', 'ও': 'I', 'ঔ': 'J',
    'ক': 'K', 'খ': 'L', 'গ': 'M', 'ঘ': 'N', 'ঙ': 'O',
    'চ': 'P', 'ছ': 'Q', 'জ': 'R', 'ঝ': 'S', 'ঞ': 'T',
    'ট': 'U', 'ঠ': 'V', 'ড': 'W', 'ঢ': 'X', 'ণ': 'Y',
    'ত': 'Z', 'থ': '_', 'দ': '`', 'ধ': 'a', 'ন': 'b',
    'প': 'c', 'ফ': 'd', 'ব': 'e', 'ভ': 'f', 'ম': 'g',
    'য': 'h', 'র': 'i', 'ল': 'j', 'শ': 'k', 'ষ': 'l',
    'স': 'm', 'হ': 'n', 'ড়': 'o', 'ঢ়': 'p', 'য়': 'q',
    'ৎ': 'r', 'ং': 's', 'ঃ': 't', 'ঁ': 'u',
    '০': '0', '১': '1', '২': '2', '৩': '3', '৪': '4',
    '৫': '5', '৬': '6', '৭': '7', '৮': '8', '৯': '9',
    'া': 'v', 'ী': 'x', 'ু': 'y', 'ূ': '~', 'ৃ': '„',
    '।': '|', '্': '&'
  };

  function unicodeToBijoy(text) {
    if (!text) return '';

    function convertBengaliRun(bText) {
      let s = bText;

      // 1. Conjuncts
      for (const [uConj, bConj] of uToBConjuncts) {
        s = s.split(uConj).join(bConj);
      }

      // 2. Ra-fola / Ya-fola / Ba-fola
      s = s.replace(/([ক-হ])্\s*র/g, '$1ª');
      s = s.replace(/([ক-হ])্\s*য/g, '$1¨');
      s = s.split('্য').join('¨');
      s = s.replace(/([ক-হ])্\s*ব/g, '$1^');

      // 3. Pre-kar reordering
      const CLUSTER = '((?:[ক-হa-zA-Z\u00C0-\u017F²³´µ¶·¹º»¼½¾¿ÀÂÃÄÅÆÇÈÉÊËÌÍÎÏ×ØÙÚÛÜÝÞßàáâãäåæçéêëìíîïðñòóôõö÷øùûüýþš¯ª¨^°±”][&্])*[ক-হa-zA-Z\u00C0-\u017F²³´µ¶·¹º»¼½¾¿ÀÂÃÄÅÆÇÈÉÊËÌÍÎÏ×ØÙÚÛÜÝÞßàáâãäåæçéêëìíîïðñòóôõö÷øùûüýþš¯ª¨^°±”])';
      const clusterRe = new RegExp(CLUSTER, 'g');

      // Ref with pre-kars
      s = s.replace(new RegExp('র্' + CLUSTER + 'ি', 'g'), 'w$1©');
      s = s.replace(new RegExp('র্' + CLUSTER + 'ে', 'g'), '†$1©');
      s = s.replace(new RegExp('র্' + CLUSTER + 'ৈ', 'g'), 'ˆ$1©');
      // Ref alone
      s = s.replace(new RegExp('র্' + CLUSTER, 'g'), '$1©');

      // Standard Pre-kars
      s = s.replace(new RegExp(CLUSTER + 'ো', 'g'), '†$1v');
      s = s.replace(new RegExp(CLUSTER + 'ৌ', 'g'), '†$1Š');
      s = s.replace(new RegExp(CLUSTER + 'ে', 'g'), '†$1');
      s = s.replace(new RegExp(CLUSTER + 'ি', 'g'), 'w$1');
      s = s.replace(new RegExp(CLUSTER + 'ৈ', 'g'), 'ˆ$1');

      // Handle য়
      s = s.split('য়').join('q');
      s = s.split('য়').join('q');

      // 4. Map individual characters
      const chars = [];
      for (const ch of s) {
        chars.push(uToBChars[ch] || ch);
      }
      return chars.join('');
    }

    // Process only Unicode Bengali runs, keeping English words and code 100% UNTOUCHED
    const parts = text.split(/([\u0980-\u09FF]+)/);
    const converted = parts.map(p => /[\u0980-\u09FF]/.test(p) ? convertBengaliRun(p) : p);
    return converted.join('');
  }

  function convertUnicodeToBijoyMarkdown(markdownText) {
    if (!markdownText) return '';

    // Protect code blocks
    const codeBlocks = [];
    let text = markdownText.replace(/```[\s\S]*?```/g, m => {
      codeBlocks.push(m);
      return `__CODE_BLOCK_${codeBlocks.length - 1}__`;
    });

    // Protect inline code
    const inlineCodes = [];
    text = text.replace(/`[^`\n]+`/g, m => {
      inlineCodes.push(m);
      return `__INLINE_CODE_${inlineCodes.length - 1}__`;
    });

    // Protect URLs
    const urls = [];
    text = text.replace(/\[(.*?)\]\((https?:\/\/[^\s)]+|file:\/\/[^\s)]+|\/[^\s)]+)\)/g, (m, txt, url) => {
      urls.push(url);
      return `[${txt}](__URL_${urls.length - 1}__)`;
    });

    let converted = unicodeToBijoy(text);

    urls.forEach((u, idx) => { converted = converted.replace(`__URL_${idx}__`, u); });
    inlineCodes.forEach((ic, idx) => { converted = converted.replace(`__INLINE_CODE_${idx}__`, ic); });
    codeBlocks.forEach((cb, idx) => { converted = converted.replace(`__CODE_BLOCK_${idx}__`, cb); });

    return converted;
  }

  return {
    convert: convert,
    convertMarkdown: convertMarkdown,
    unicodeToBijoy: unicodeToBijoy,
    convertUnicodeToBijoyMarkdown: convertUnicodeToBijoyMarkdown,
    isLikelyBijoy: isLikelyBijoy,
    isBijoyToken: isBijoyToken,
  };
})();
