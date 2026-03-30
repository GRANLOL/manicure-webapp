import http from 'k6/http';
import { check, sleep } from 'k6';

const baseUrl = (__ENV.BASE_URL || 'http://127.0.0.1:8000/api').replace(/\/$/, '');
const authHeader = __ENV.TG_INIT_DATA || '';

const serviceId = Number(__ENV.SERVICE_ID || 0);
const serviceName = (__ENV.SERVICE_NAME || '').trim();
const bookingDate = (__ENV.BOOKING_DATE || '').trim();
const uniqueTimes = (__ENV.UNIQUE_TIMES || '').split(',').map((item) => item.trim()).filter(Boolean);
const conflictTime = (__ENV.CONFLICT_TIME || '').trim();
const phonePrefix = (__ENV.PHONE_PREFIX || '+7999000').trim();
const scheduleInterval = Number(__ENV.SCHEDULE_INTERVAL || 30);

function buildHeaders() {
    const headers = {
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': 'true',
    };

    if (authHeader) {
        headers['X-Telegram-Init-Data'] = authHeader;
    }

    return headers;
}

function buildPhone(vu, iter) {
    const suffix = String(vu * 1000 + iter).padStart(4, '0');
    return `${phonePrefix}${suffix}`;
}

function buildBookingPayload({ slotTime, vu, iter }) {
    return {
        service_id: serviceId || undefined,
        service: serviceName || undefined,
        date: bookingDate,
        time: slotTime,
        duration: scheduleInterval,
        price: 0,
        phone: buildPhone(vu, iter),
        name: `Load Test ${vu}-${iter}`,
    };
}

export const options = {
    scenarios: {
        browse: {
            executor: 'constant-vus',
            vus: Number(__ENV.BROWSE_VUS || 10),
            duration: __ENV.BROWSE_DURATION || '30s',
            exec: 'browseScenario',
            tags: { scenario_type: 'browse' },
        },
        unique_booking: {
            executor: 'per-vu-iterations',
            vus: Number(__ENV.UNIQUE_BOOKING_VUS || Math.max(uniqueTimes.length, 1)),
            iterations: Number(__ENV.UNIQUE_BOOKING_ITERATIONS || 1),
            startTime: __ENV.UNIQUE_BOOKING_START || '2s',
            exec: 'uniqueBookingScenario',
            tags: { scenario_type: 'unique_booking' },
        },
        conflict_booking: {
            executor: 'per-vu-iterations',
            vus: Number(__ENV.CONFLICT_VUS || 10),
            iterations: Number(__ENV.CONFLICT_ITERATIONS || 1),
            startTime: __ENV.CONFLICT_START || '4s',
            exec: 'conflictBookingScenario',
            tags: { scenario_type: 'conflict_booking' },
        },
    },
    thresholds: {
        http_req_failed: ['rate<0.05'],
        http_req_duration: ['p(95)<1500'],
        'http_req_duration{scenario_type:browse}': ['p(95)<800'],
        'checks{scenario_type:browse}': ['rate>0.99'],
    },
};

export function setup() {
    const headers = buildHeaders();
    const contentResponse = http.get(`${baseUrl}/get-content`, { headers, tags: { endpoint: 'get-content', phase: 'setup' } });
    check(contentResponse, {
        'setup get-content ok': (res) => res.status === 200,
    });

    const content = contentResponse.status === 200 ? contentResponse.json() : {};
    const firstService = Array.isArray(content.services) && content.services.length > 0 ? content.services[0] : null;

    const resolvedServiceId = serviceId || Number(firstService?.id || 0);
    const resolvedServiceName = serviceName || String(firstService?.name || '');

    if (!resolvedServiceId && !resolvedServiceName) {
        throw new Error('No service configured. Set SERVICE_ID or ensure /api/get-content returns services.');
    }

    if (!bookingDate) {
        console.warn('BOOKING_DATE is not set. Browse scenario will work, booking scenarios will likely fail validation.');
    }

    if (uniqueTimes.length === 0) {
        console.warn('UNIQUE_TIMES is empty. unique_booking scenario will reuse conflict time or skip meaningful booking checks.');
    }

    return {
        headers,
        serviceId: resolvedServiceId,
        serviceName: resolvedServiceName,
        bookingDate,
        uniqueTimes,
        conflictTime,
    };
}

export function browseScenario(data) {
    const health = http.get(`${baseUrl}/health`, { headers: data.headers, tags: { endpoint: 'health' } });
    check(health, {
        'health 200': (res) => res.status === 200,
    });

    const content = http.get(`${baseUrl}/get-content`, { headers: data.headers, tags: { endpoint: 'get-content' } });
    check(content, {
        'get-content 200': (res) => res.status === 200,
        'get-content has services': (res) => {
            const body = res.json();
            return Array.isArray(body.services);
        },
    });

    const slots = http.get(`${baseUrl}/busy-slots`, { headers: data.headers, tags: { endpoint: 'busy-slots' } });
    check(slots, {
        'busy-slots 200': (res) => res.status === 200,
    });

    sleep(Number(__ENV.BROWSE_SLEEP || 1));
}

export function uniqueBookingScenario(data) {
    if (!data.bookingDate) {
        return;
    }

    const slotTime = data.uniqueTimes[(__VU - 1) % Math.max(data.uniqueTimes.length, 1)] || data.conflictTime;
    if (!slotTime) {
        return;
    }

    const payload = JSON.stringify({
        ...buildBookingPayload({ slotTime, vu: __VU, iter: __ITER }),
        service_id: data.serviceId || undefined,
        service: data.serviceName || undefined,
        date: data.bookingDate,
    });

    const response = http.post(`${baseUrl}/bookings`, payload, {
        headers: data.headers,
        tags: { endpoint: 'bookings', booking_mode: 'unique' },
    });

    check(response, {
        'unique booking accepted': (res) => res.status === 200,
    });
}

export function conflictBookingScenario(data) {
    if (!data.bookingDate || !data.conflictTime) {
        return;
    }

    const payload = JSON.stringify({
        ...buildBookingPayload({ slotTime: data.conflictTime, vu: __VU, iter: __ITER }),
        service_id: data.serviceId || undefined,
        service: data.serviceName || undefined,
        date: data.bookingDate,
    });

    const response = http.post(`${baseUrl}/bookings`, payload, {
        headers: data.headers,
        tags: { endpoint: 'bookings', booking_mode: 'conflict' },
    });

    check(response, {
        'conflict request handled predictably': (res) => res.status === 200 || res.status === 409,
    });
}
