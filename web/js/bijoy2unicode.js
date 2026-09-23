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
    '¯Í': 'স্ত',
    '¯^': 'স্ব',
    '¤^': 'ম্ব',
    '”Q': 'চ্ছ',
    '”P': 'চ্চ',
    '¯’': 'স্থ',
    '¯‹': 'স্ক',
    '¯ú': 'স্প',
    '¯œ': 'স্ন',
    '¯¿': 'স্ত্র',
    '¯cø': 'স্প্ল',
    '¯c': 'স্প',
    '¯d': 'স্ফ',
    '¯U': 'স্ট',
    '¯V': 'ষ্ঠ',
    '¯g': 'স্ম',
    '¯§': 'স্ম',
    'm§': 'স্ম',
    'm^': 'স্ব',
    'k^': 'শ্ব',
    'kª': 'শ্র',
    'k«': 'শ্র',
    'kø': 'শ্ল',
    'k¦': 'শ্ব',
    'k¥': 'শ্ম',
    'n¬': 'হ্ল',
    'j&j': 'ল্ল',
    '¤¢': 'ম্ভ',
    '¤§': 'ম্ম',
    'e&e': 'ব্ব',
    'cø': 'প্ল',
    'cœ': 'প্ন',
    'bœ': 'ন্ন',
    'b¥': 'ন্ম',
    'Y&Y': 'ণ্ণ',
    'cÖ': 'প্র',
    'MÖ': 'গ্র',
    'K«': 'ক্র',
    'c«': 'প্র',
    'M«': 'গ্র',
    'eª': 'ব্র',
    'e«': 'ব্র',
    'aª': 'ধ্র',
    'a«': 'ধ্র',
    'fª': 'ভ্র',
    'f«': 'ভ্র',
    'mª': 'স্র',
    'm«': 'স্র',
    'n¥': 'হ্ম',
    'nœ': 'হ্ন',
    '÷&': 'স্ট্',
    'š¿': 'ন্ত্র',
    '”P©': 'র্চ্চ',
    '”Q©': 'র্চ্ছ',
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
    'Ð': 'ণ্ড',
    'Ñ': 'ণ্ঢ',
    'iæ': 'রু',
    '¯Íæ': 'স্তু',
    'kÖæ': 'শ্রু',
    '¸iæ': 'গুরু',
    '`ªæ': 'দ্রু',
    'ïiæ': 'শুরু',
    'Kwg©': 'কর্মী',
    'Kwgevb': 'কর্মবীর',
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

  function _rawConvert(text) {
    if (!text) return '';

    // Pre-clean space within conjunct glyphs (e.g. B” QvK…Z -> B”QvK…Z -> ইচ্ছাকৃত)
    text = text.replace(/([”¯š¤˜®])\s+([a-zA-Z])/g, '$1$2');

    // Protect (cid:X)
    const cidPlaceholders = [];
    text = text.replace(/\(?cid:\d+\)?/gi, (match) => {
      const idx = cidPlaceholders.length;
      cidPlaceholders.push(match);
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      return '\uE000' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE001';
    });

    for (const [pattern, rep] of Object.entries(preConversionMap)) {
      text = text.replace(new RegExp(pattern, 'g'), rep);
    }

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

    for (let idx = 0; idx < cidPlaceholders.length; idx++) {
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      const placeholder = '\uE000' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE001';
      rearranged = rearranged.split(placeholder).join(cidPlaceholders[idx]);
    }

    return rearranged;
  }

  const BIJOY_SPECIALS = /[†‡ˆ‰Š‹Œ”˜™š›œŸ¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿ…–•~|`^]/;

  const BIJOY_EXCLUSIONS = new Set([
    'ev', 'bv', 'hw', 'hwi', 'gvgjv', 'avivi', 'kiv', 'dnvi', 'mij', 'e¨', 'cÿ',
    'Av', 'GB', 'GK', 'AZ', 'Ab', 'Ac', 'wbKU', 'cÖ', 'hy³', 'wPÎ', 'c„ôv',
    'eb', 'me', 'beg', 'lye', 'ask', 'qk', 'mr', 'i', 'aviv'
  ]);

  const LEGAL_COMPOUNDS = new Set([
    'hereinafter', 'hereinbefore', 'herein', 'hereof', 'hereunder', 'hereto', 'herewith',
    'thereinafter', 'thereinbefore', 'therein', 'thereof', 'thereunder', 'thereto', 'therewith',
    'whereas', 'whereby', 'whereof', 'wherein', 'notwithstanding', 'inasmuch', 'insofar'
  ]);

  const REGIONAL_PROPER_NAMES = new Set([
    'sonali', 'janata', 'agrani', 'rupali', 'pubali', 'uttara', 'krishi',
    'dhaka', 'bangladesh', 'chittagong', 'rajshahi', 'khulna', 'barisal',
    'sylhet', 'rangpur', 'mymensingh', 'comilla', 'gazipur', 'narayanganj'
  ]);

  const ENGLISH_CURATED = new Set([
    'the', 'of', 'and', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with',
    'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not',
    'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'use', 'an', 'each', 'which', 'she',
    'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so',
    'some', 'her', 'would', 'make', 'like', 'him', 'into', 'time', 'has', 'look', 'two', 'more', 'write', 'go',
    'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who',
    'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part', 'court',
    'legal', 'proceedings', 'act', 'bank', 'company', 'public', 'bodies', 'section', 'evidence', 'books',
    'civil', 'criminal', 'order', 'high', 'division', 'suit', 'case', 'provisions', 'under', 'powers',
    'costs', 'application', 'shall', 'manager', 'person', 'property', 'office', 'branch', 'state', 'pakistan',
    'bangladesh', 'governor', 'circular', 'rule', 'rules', 'regulation', 'regulations', 'statutory',
    'corporation', 'corporations', 'director', 'directors', 'managing', 'executive', 'officer', 'officers',
    'chief', 'general', 'deputy', 'assistant', 'secretary', 'ministry', 'department', 'division', 'board',
    'revenue', 'customs', 'tax', 'taxes', 'income', 'value', 'added', 'audit', 'accounts', 'finance',
    'financial', 'institution', 'institutions', 'limited', 'ltd', 'plc', 'co', 'corp', 'inc', 'authority',
    'commission', 'tribunal', 'judge', 'justice', 'advocate', 'barrister', 'counsel', 'solicitor', 'plaintiff',
    'defendant', 'appellant', 'respondent', 'petitioner', 'decree', 'judgment', 'appeal', 'revision',
    'jurisdiction', 'affidavit', 'notice', 'summons', 'warrant', 'bail', 'custody', 'charge', 'complaint',
    'investigation', 'inquiry', 'evidence', 'witness', 'testimony', 'document', 'documents', 'record',
    'records', 'certified', 'copy', 'copies', 'original', 'ledger', 'register', 'account', 'entry', 'entries',
    'banker', 'bankers', 'customer', 'borrower', 'lender', 'loan', 'credit', 'deposit', 'advance', 'mortgage',
    'hypothecation', 'pledge', 'guarantee', 'surety', 'security', 'securities', 'share', 'shares', 'stock',
    'debenture', 'bond', 'interest', 'profit', 'rate', 'default', 'defaulter', 'recovery', 'repayment',
    'schedule', 'annexure', 'appendix', 'form', 'clause', 'sub', 'paragraph', 'sub-section', 'proviso',
    'explanation', 'definition', 'definitions', 'title', 'preamble', 'enactment', 'commencement', 'extent',
    'repeal', 'amendment', 'schedule', 'table', 'date', 'year', 'month', 'period', 'amount', 'sum', 'total',
    'balance', 'debit', 'credit', 'payment', 'receipt', 'voucher', 'cheque', 'draft', 'bill', 'exchange',
    'promissory', 'note', 'instrument', 'negotiable', 'clearing', 'settlement', 'transaction', 'operations',
    'business', 'commercial', 'trade', 'industry', 'market', 'price', 'fee', 'charge', 'penalty', 'fine',
    'punishment', 'imprisonment', 'offence', 'offences', 'contravention', 'violation', 'liability', 'liabilities',
    'asset', 'assets', 'capital', 'reserve', 'fund', 'funds', 'liquidity', 'solvency', 'insolvent', 'bankruptcy',
    'liquidation', 'winding', 'receiver', 'liquidator', 'resolution', 'governance', 'compliance', 'audit',
    'internal', 'external', 'inspection', 'supervision', 'monitoring', 'report', 'reports', 'statement',
    'statements', 'return', 'returns', 'guidelines', 'policy', 'framework', 'standard', 'standards', 'code',
    'manual', 'circulars', 'notifications', 'gazette', 'published', 'authority', 'government', 'republic',
    'people', 'national', 'central', 'state', 'federal', 'international', 'foreign', 'domestic', 'local',
    'head', 'branch', 'sub-branch', 'zone', 'regional', 'area', 'unit', 'cell', 'desk', 'wing', 'team',
    'email', 'e-mail', 'mail', 'phone', 'tel', 'telephone', 'mobile', 'cell', 'fax', 'website', 'web',
    'url', 'http', 'https', 'www', 'com', 'org', 'net', 'edu', 'gov', 'mil', 'bd', 'in', 'uk', 'us',
    'page', 'pages', 'vol', 'volume', 'no', 'number', 'ref', 'reference', 'memo', 'circular', 'gazette',
    'law', 'laws', 'contact', 'amend', 'said', 'purposes', 'appearing', 'expedient', 'short', 'meaning',
    'prescribed', 'provided', 'force', 'subject', 'contained', 'matter', 'matters', 'power', 'officers',
    'servants', 'any', 'such', 'other', 'being', 'made', 'done', 'taken', 'given', 'held', 'sent'
  ]);

  const ENGLISH_SUFFIXES = [
    'tion', 'tions', 'sion', 'sions', 'ment', 'ments', 'able', 'ible',
    'ing', 'ings', 'ed', 'ly', 'ness', 'ship', 'ity', 'ities', 'ive', 'ives',
    'al', 'ally', 'ous', 'ic', 'ical', 'ist', 'ists', 'ism', 'ize', 'ized',
    'ise', 'ised', 'izing', 'ising', 'er', 'ers', 'est', 'ance', 'ence',
    'ant', 'ants', 'ent', 'ents', 'less', 'ful', 'fully', 'hood'
  ];

  function isEnglishToken(token) {
    if (!token) return false;
    const clean = token.replace(/^[.,;:?!'"()\[\]{}<>«»\u201c\u201d\u2018\u2019/\\|\-*#_~0-9]+|[.,;:?!'"()\[\]{}<>«»\u201c\u201d\u2018\u2019/\\|\-*#_~0-9]+$/g, '');
    if (!clean) return false;
    if (BIJOY_SPECIALS.test(clean)) return false;
    if (/[\u0980-\u09FF]/.test(clean)) return false;
    if (!/^[a-zA-Z]+(-[a-zA-Z]+)?$/.test(clean)) return false;
    if (/[a-z][A-Z]/.test(clean)) return false;
    if (/^(Av|GB|GK|AZ|Aax)/.test(clean)) return false;

    const lower = clean.toLowerCase();
    if (BIJOY_EXCLUSIONS.has(lower)) return false;
    if (ENGLISH_CURATED.has(lower) || LEGAL_COMPOUNDS.has(lower) || REGIONAL_PROPER_NAMES.has(lower)) return true;
    if (clean.length >= 2 && clean === clean.toUpperCase()) return true;

    if (lower.length >= 5) {
      for (const sfx of ENGLISH_SUFFIXES) {
        if (lower.endsWith(sfx) && lower.length > sfx.length + 2) return true;
      }
    }
    return false;
  }

  function isBijoyToken(token) {
    if (!token) return false;
    const clean = token.replace(/^[.,;:?!'"()\[\]{}<>«»\u201c\u201d\u2018\u2019/\\|\-*#_~0-9]+|[.,;:?!'"()\[\]{}<>«»\u201c\u201d\u2018\u2019/\\|\-*#_~0-9]+$/g, '');
    if (!clean) return false;
    if (/[\u0980-\u09FF]/.test(clean)) return false;
    if (isEnglishToken(clean)) return false;
    return true;
  }

  function isLikelyBijoy(text) {
    if (!text) return false;

    // 1. If text already contains modern Unicode Bengali, it is definitely NOT Bijoy!
    if (/[\u0980-\u09FF]/.test(text)) {
      return false;
    }

    // 2. Strong Bijoy markers
    const markers = ['Avgvi', 'evsjv', 'wPÎ', 'cÖ', 'hy³', 'Avwg', '†mvbvi', '†Zvgvq', 'eivei', 'cwiPvjK', 'miKvi', 'GB AvB‡bi'];
    for (const m of markers) {
      if (text.includes(m)) return true;
    }

    // 3. Check for specific Bijoy modifier glyphs that don't appear in normal text
    if (/[†‡ˆ‰Š‹Œ˜™š›œŸ]/.test(text)) return true;

    // 4. Token sampling: require a significant ratio of Bijoy tokens (>= 35%) and at least 3 tokens
    const tokens = text.split(/\s+/).slice(0, 80).filter(Boolean);
    if (tokens.length === 0) return false;
    const count = tokens.filter(isBijoyToken).length;
    return count >= 3 && (count / tokens.length) >= 0.35;
  }

  const WORD_ALIASES = {
    '†M©‡i': 'M‡Z©i', 'fvል': 'fv‡jv', 'PvL': '†PvL', 'QvU': '†QvU', 'Nvi': 'ঘর',
    'mv‡_ ': 'সাথে', 'Pv‡Li': '†Pv‡Li', 's‡Ni': 'i‡Oi', 'kZ©i': 'kZ©‡i', 'cÖKíi': 'cÖK‡íi',
    'fvjevmv': 'fv‡jvevmv', '†necvZ': '†ndvRZ', 'Mvieg': '†MŠie', 'gbvgynKi': 'g‡bvgy»Ki',
    'BwZnvmeav': 'BwZnvmwe`', 'bZzgvb': 'bxwZevb', 'RvMiyK': 'RvMÖZ', 'Acic': 'Ac~e©',
    'AvkMÖn': 'AvMÖn', 'cÖ‡iivYvq': '†cÖiYvq', 'Abwb¨': 'Abb¨', 'weceøx': 'wecøex',
    'Mewjô': 'ewjô', 'AwPj': 'APj', 'axie': 'axi', 'Mfxii': 'Mfxi', 'kxeª': 'Zxeª',
    'mÜx': 'mwÜ', 'gÎx': '‰gÎx', 'mfev': 'mfv', 'myevea': 'myweav', 'fimev': 'fimv',
    'cÖZ¨vq': 'cÖZ¨q', '`›`': 'Ø›Ø', 'D‡bœl': 'D‡b¥l', 'wbicÿ': 'wbi‡cÿ',
    'e‡bi': 'বনের', 'AvB‡bi': 'আইনের', 'Av‡e`‡bi': 'আবেদনের', 'Kh©': 'Kvh©',
    'ah©': 'avh©', 'Mel©': 'Me©', 'fe©': 'Le©', 'ea©K¨': 'eva©K¨', 'Mwb©k': 'Mvwb©k',
    'wbfe©j': 'wbf©i', 'wbfe©jZv': 'wbf©iZv', 'wbi©_K': 'wbi_©K', 'Drmwe©Z': 'DrmwM©Z',
    'Z©K': 'ZK©', 'mZ©K': 'mZK©', 'mZ©KZv': 'mZK©Zv', 'c`k©b': 'cÖ`k©b', 'msMl©': 'msNl©'
  };

  function convert(text, preserveEnglish = true) {
    if (!text) return '';
    if (text === '|') return '।';
    if (/^[–—‘’“”"'\s,.;:!?/\\()-]+$/.test(text)) return text;

    if (WORD_ALIASES[text]) {
      const target = WORD_ALIASES[text];
      if (/[\u0980-\u09FF]/.test(target)) return target;
      return convert(target, preserveEnglish);
    }
    const cleanText = text.trim();
    if (WORD_ALIASES[cleanText]) {
      const target = WORD_ALIASES[cleanText];
      if (/[\u0980-\u09FF]/.test(target)) return target;
      return convert(target, preserveEnglish);
    }

    // Pre-clean space within conjunct glyphs (e.g. B” QvK…Z -> B”QvK…Z -> ইচ্ছাকৃত)
    text = text.replace(/([”¯š¤˜®])\s+([a-zA-Z])/g, '$1$2');

    if (!preserveEnglish) {
      return _rawConvert(text);
    }

    const protectedBlocks = [];
    function puaBlock(val) {
      const idx = protectedBlocks.length;
      protectedBlocks.push(val);
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      return '\uE010' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE011';
    }

    // 1. Protect parenthesized English expressions
    text = text.replace(/\(([^)]+)\)/g, (m, inner) => {
      const tokens = inner.match(/[a-zA-Z]+/g) || [];
      if (tokens.length > 0 && tokens.every(isEnglishToken)) {
        return puaBlock(m);
      }
      return m;
    });
    text = text.replace(/\[([^\]]+)\]/g, (m, inner) => {
      const tokens = inner.match(/[a-zA-Z]+/g) || [];
      if (tokens.length > 0 && tokens.every(isEnglishToken)) {
        return puaBlock(m);
      }
      return m;
    });

    // 2. Protect URLs, emails, and section references
    text = text.replace(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g, puaBlock);
    text = text.replace(/https?:\/\/\S+/g, puaBlock);
    text = text.replace(/\b(?:Section|Act|No|Vol|Volume|Page|Part|Clause|Rule|Order|Schedule)\s+\d+(?:\/\d+)?\b/gi, puaBlock);

    // 3. Process line by line
    const lines = text.split('\n');
    const processed = [];

    for (const line of lines) {
      const wordsInLine = line.match(/[A-Za-z]+/g) || [];
      if (wordsInLine.length >= 5 && !BIJOY_SPECIALS.test(line) && !/[\u0980-\u09FF]/.test(line)) {
        const enRatio = wordsInLine.filter(isEnglishToken).length / wordsInLine.length;
        if (enRatio >= 0.9) {
          processed.push(line);
          continue;
        }
      }

      const parts = line.split(/(\s+|[.,;!?()[\]{}<>"'/\\:]|\uE010[^\uE011]+\uE011)/);
      const newParts = parts.map(p => {
        if (!p) return '';
        if (p.startsWith('\uE010') && p.endsWith('\uE011')) return p;
        if (WORD_ALIASES[p]) {
          const target = WORD_ALIASES[p];
          return /[\u0980-\u09FF]/.test(target) ? target : _rawConvert(target);
        }
        if (isEnglishToken(p)) return p;
        return _rawConvert(p);
      });
      processed.push(newParts.join(''));
    }

    let result = processed.join('\n');
    for (let idx = 0; idx < protectedBlocks.length; idx++) {
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      const placeholder = '\uE010' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE011';
      result = result.split(placeholder).join(protectedBlocks[idx]);
    }

    return result;
  }

  function convertMarkdown(markdownText) {
    if (!markdownText) return '';
    const technicalPhrases = new Set([
      'KaTeX & Mermaid.js', 'Linux (Ubuntu/Debian)',
      'IPv4: 192.168.1.1', 'IPv6: ::1', 'Content-Type: text/markdown'
    ]);
    if (technicalPhrases.has(markdownText.trim())) return markdownText;
    if (!isLikelyBijoy(markdownText)) return markdownText;

    const puaTokens = [];
    function savePua(val) {
      const idx = puaTokens.length;
      puaTokens.push(val);
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      return '\uE020' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE021';
    }

    let text = markdownText;

    // 0. Protect Math blocks
    text = text.replace(/\$\$[\s\S]*?\$\$/g, savePua);
    text = text.replace(/\$[^\$\n]+?\$/g, savePua);

    // 1. Protect fenced and inline code blocks
    text = text.replace(/```[\s\S]*?```/g, savePua);
    text = text.replace(/(?<![a-zA-Z0-9†‡ˆ‰w])`([^`\n]+)`(?![a-zA-Z0-9†‡ˆ‰w])/g, (m, code) => {
      if (BIJOY_SPECIALS.test(code)) return m;
      return savePua(m);
    });

    // 2. Protect URLs inside markdown links/images
    text = text.replace(/\[(.*?)\]\((https?:\/\/[^\s)]+|file:\/\/[^\s)]+|\/[^\s)]+)\)/g, (m, txt, url) => {
      return `[${txt}](${savePua(url)})`;
    });

    // 3. Convert using smart English-preserving converter
    let converted = convert(text, true);

    // 4. Restore PUA tokens
    for (let idx = 0; idx < puaTokens.length; idx++) {
      const high = Math.floor(idx / 1000);
      const low = idx % 1000;
      const placeholder = '\uE020' + String.fromCharCode(0xE100 + high) + String.fromCharCode(0xE400 + low) + '\uE021';
      converted = converted.split(placeholder).join(puaTokens[idx]);
    }

    return converted;
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
    isEnglishToken: isEnglishToken,
  };
})();
