type MeetingItem = {
  recording_id?: number;
  title?: string;
  meeting_title?: string;
  created_at?: string;
  share_url?: string;
  recorded_by?: {
    name?: string;
    email?: string;
  };
};

type MeetingsResponse = {
  limit?: number | null;
  next_cursor?: string | null;
  items?: MeetingItem[];
};

const apiKey = process.env.FATHOM_API_KEY;

if (!apiKey) {
  throw new Error('Нужно задать переменную окружения FATHOM_API_KEY');
}

const baseUrl = 'https://api.fathom.ai/external/v1/meetings';
const createdAfter = process.env.FATHOM_CREATED_AFTER;
const createdBefore = process.env.FATHOM_CREATED_BEFORE;
const includeTranscript = process.env.FATHOM_INCLUDE_TRANSCRIPT === 'true';
const includeSummary = process.env.FATHOM_INCLUDE_SUMMARY === 'true';
const maxPages = Number(process.env.FATHOM_MAX_PAGES ?? '2');

async function fetchPage(cursor?: string): Promise<MeetingsResponse> {
  const url = new URL(baseUrl);

  if (cursor) {
    url.searchParams.set('cursor', cursor);
  }
  if (createdAfter) {
    url.searchParams.set('created_after', createdAfter);
  }
  if (createdBefore) {
    url.searchParams.set('created_before', createdBefore);
  }
  if (includeTranscript) {
    url.searchParams.set('include_transcript', 'true');
  }
  if (includeSummary) {
    url.searchParams.set('include_summary', 'true');
  }

  const response = await fetch(url, {
    headers: {
      'X-Api-Key': apiKey,
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`Fathom API error ${response.status}: ${body}`);
  }

  return (await response.json()) as MeetingsResponse;
}

async function main(): Promise<void> {
  let cursor: string | undefined;
  let pageNumber = 0;

  while (pageNumber < maxPages) {
    const page = await fetchPage(cursor);
    pageNumber += 1;

    console.log(`\n=== Page ${pageNumber} ===`);
    for (const item of page.items ?? []) {
      console.log(JSON.stringify({
        recording_id: item.recording_id,
        title: item.title,
        meeting_title: item.meeting_title,
        created_at: item.created_at,
        share_url: item.share_url,
        recorded_by: item.recorded_by,
      }, null, 2));
    }

    if (!page.next_cursor) {
      break;
    }
    cursor = page.next_cursor;
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
