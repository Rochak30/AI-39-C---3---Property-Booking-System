* ============================================================
   BOOKMANDU — SHARED APP.JS
   All shared data, state, utilities, and UI helpers.
   Include this in every page via base.html.
   ============================================================ */

// ============================================================
// DATA
// ============================================================

/**
 * PROPERTIES - Master array of all property listings
 * Contains all property data including:
 * - Basic info: id, title, region, type, price
 * - Guest info: maxGuests, amenities, host
 * - Ratings: rating, reviews, bookings
 * - Visual: icon, trending flag
 * - Safety: safety information
 * - Description: detailed property description
 * - Availability: bookedDates array
 */
const PROPERTIES = [
  { id:1, title:"Mountain View Homestay", region:"Kathmandu", type:"Homestay", price:3200, maxGuests:4, rating:4.8, reviews:24, bookings:47, icon:"🏔", trending:true, amenities:["WiFi","Breakfast","Hot Water","Mountain View"], host:"Sita Rai", safety:"Fire extinguisher on each floor. Emergency exits marked. No smoking indoors.", desc:"A beautiful traditional Newari homestay with stunning views of the Himalayan range. Located 20 minutes from Thamel, this family-run property offers authentic Nepali hospitality with modern comforts. Enjoy home-cooked Newari meals and personalised cultural tours.", bookedDates:[[2026,5,20],[2026,5,21],[2026,5,22],[2026,6,1],[2026,6,2]] },
  { id:2, title:"Thamel Heritage House", region:"Kathmandu", type:"Guesthouse", price:2800, maxGuests:6, rating:4.6, reviews:18, bookings:31, icon:"🕌", trending:false, amenities:["WiFi","Kitchen Access","Parking","Hot Water"], host:"Bikash Shrestha", safety:"CCTV in common areas. 24/7 reception. First aid kit available.", desc:"A charming heritage guesthouse in the heart of Thamel. Originally built in the 1950s, this property blends traditional architecture with comfortable modern amenities. Walk to restaurants, shops, and cultural sites within minutes.", bookedDates:[[2026,5,25],[2026,5,26],[2026,5,27]] },
  { id:3, title:"Lakeside Comfort Inn", region:"Pokhara", type:"Private Room", price:1800, maxGuests:2, rating:4.9, reviews:41, bookings:89, icon:"🏞", trending:true, amenities:["WiFi","Breakfast","Lake View","Hot Water"], host:"Puja Gurung", safety:"Life jackets provided for lake activities. First aid station at reception.", desc:"Wake up to breathtaking views of Phewa Lake from your private room. This boutique property is just steps from the lakeside promenade. Perfect for honeymooners and solo travellers seeking tranquility.", bookedDates:[[2026,5,18],[2026,5,19],[2026,5,23],[2026,5,24]] },
  { id:4, title:"Pakhribas Valley Cottage", region:"Chitwan", type:"Entire Property", price:5500, maxGuests:10, rating:4.7, reviews:12, bookings:22, icon:"🌿", trending:false, amenities:["WiFi","Kitchen Access","Parking","Garden"], host:"Mani Tharu", safety:"Property is fenced. Jungle safari guide available. Emergency contact provided.", desc:"An entire private cottage surrounded by lush vegetation near Chitwan National Park. Perfect for families or groups who want an immersive nature experience with jungle safaris and bird watching.", bookedDates:[[2026,6,10],[2026,6,11],[2026,6,12]] },
  { id:5, title:"Annapurna Base Retreat", region:"Mustang", type:"Homestay", price:4200, maxGuests:3, rating:4.5, reviews:9, bookings:15, icon:"🗻", trending:false, amenities:["Breakfast","Hot Water","Mountain View","Parking"], host:"Dawa Lama", safety:"Altitude sickness awareness guide provided. Oxygen available on request.", desc:"Experience the raw beauty of Upper Mustang from this traditional stone house. Located at 3800m, surrounded by dramatic red-rock canyons and ancient Buddhist monasteries.", bookedDates:[[2026,5,28],[2026,5,29]] },
  { id:6, title:"Boudha Stupa View Room", region:"Kathmandu", type:"Private Room", price:2200, maxGuests:2, rating:4.4, reviews:33, bookings:61, icon:"🧘", trending:true, amenities:["WiFi","Breakfast","Temple View","Hot Water"], host:"Nyima Sherpa", safety:"No sharp objects near meditation area. Quiet hours 9pm–7am.", desc:"A peaceful private room with a rooftop terrace overlooking the magnificent Boudha Stupa. Ideal for spiritual seekers, meditators, and those wanting to experience Tibetan Buddhist culture up close.", bookedDates:[[2026,6,5],[2026,6,6]] },
  { id:7, title:"Lumbini Pilgrim House", region:"Lumbini", type:"Guesthouse", price:1500, maxGuests:4, rating:4.3, reviews:27, bookings:38, icon:"🕊", trending:false, amenities:["WiFi","Breakfast","Parking","Garden"], host:"Ram Prasad", safety:"Strict no-noise policy after 10pm. Respectful dress code in sacred areas.", desc:"A serene guesthouse just 500 metres from the birthplace of Lord Buddha. Welcoming pilgrims and cultural tourists since 2010, offering a calm and respectful environment for reflection.", bookedDates:[] },
  { id:8, title:"Bandipur Hilltop Bungalow", region:"Kathmandu", type:"Entire Property", price:7500, maxGuests:8, rating:4.9, reviews:7, bookings:11, icon:"🏡", trending:false, amenities:["WiFi","Kitchen Access","Mountain View","Parking","Garden"], host:"Suresh Magar", safety:"Property equipped with fire alarm. Emergency number posted in every room.", desc:"A stunning bungalow perched on Bandipur Hill with 360-degree Himalayan views. Perfect for special occasions, family retreats, or a romantic escape. A fully equipped kitchen and private garden included.", bookedDates:[[2026,6,20],[2026,6,21],[2026,6,22],[2026,6,23]] },
];

/**
 * BOOKINGS_DATA - Sample booking data for dashboard display
 * Each booking has: reference number, property name, icon, dates, guests, status, amount
 */
const BOOKINGS_DATA = [
  { ref:"BM-A7K2M9PQ", prop:"Mountain View Homestay", icon:"🏔", dates:"May 20–23, 2026", guests:2, status:"confirmed", amount:"NPR 9,600" },
  { ref:"BM-C3L8N5RX", prop:"Lakeside Comfort Inn", icon:"🏞", dates:"Jun 5–8, 2026", guests:2, status:"pending", amount:"NPR 5,400" },
  { ref:"BM-K1P4Q7YZ", prop:"Thamel Heritage House", icon:"🕌", dates:"Mar 10–13, 2026", guests:3, status:"cancelled", amount:"NPR 8,400" },
];

// ============================================================
// STATE
// ============================================================

/** wishlist - Array of property IDs the user has saved to wishlist */
let wishlist = [1, 3, 6];

/** filterType - Current property type filter ('all', 'homestay', 'guesthouse', etc.) */
let filterType = 'all';

/** filterAmenity - Current amenity filter (null if not filtering by amenity) */
let filterAmenity = null;

/** minPrice, maxPrice - Price range filter values (null if not set) */
let minPrice = null, maxPrice = null;

/** sortBy - Current sorting method ('popular', 'price-asc', 'price-desc', 'rating') */
let sortBy = 'popular';

/**
 * Global variables for booking (will be set by property page)
 * These are shared across pages for booking functionality
 */
window.selectedCheckIn = null;      // Selected check-in date
window.selectedCheckOut = null;     // Selected check-out date
window.appliedCoupon = null;        // Currently applied coupon code
window.pricePerNight = 2500;        // Default price per night
window.availableCoupons = {         // Available coupon codes with their details
    'WELCOME10': { discount: 10, type: 'percentage', message: '10% off!', description: '10% discount applied', code: 'WELCOME10' },
    'SAVE20': { discount: 20, type: 'percentage', message: '20% off!', description: '20% discount applied', code: 'SAVE20' },
    'FLAT500': { discount: 500, type: 'fixed', message: 'NPR 500 off!', description: 'NPR 500 discount applied', code: 'FLAT500' }
};

/**
 * usedCoupons - Track used coupons in localStorage for persistence
 * This ensures coupons cannot be reused even after page refresh
 */
let usedCoupons = [];

/**
 * loadUsedCoupons - Load used coupons from localStorage
 * Called on script initialization to restore state
 * Persists coupon usage across page refreshes
 */
function loadUsedCoupons() {
    try {
        const savedUsedCoupons = localStorage.getItem('bookmandu_used_coupons');
        if (savedUsedCoupons) {
            usedCoupons = JSON.parse(savedUsedCoupons);
            console.log('Loaded used coupons from storage:', usedCoupons);
        } else {
            usedCoupons = [];
        }
    } catch(e) {
        console.log('Error loading used coupons:', e);
        usedCoupons = [];
    }
}

/**
 * saveUsedCoupons - Save used coupons to localStorage
 * Called after marking a coupon as used
 * Ensures coupon usage persists across sessions
 */
function saveUsedCoupons() {
    try {
        localStorage.setItem('bookmandu_used_coupons', JSON.stringify(usedCoupons));
        console.log('Saved used coupons to storage:', usedCoupons);
    } catch(e) {
        console.log('Error saving used coupons:', e);
    }
}

/**
 * isCouponUsed - Check if a coupon has been used already
 * @param {string} couponCode - The coupon code to check
 * @returns {boolean} - True if coupon has been used
 */
function isCouponUsed(couponCode) {
    const isUsed = usedCoupons.includes(couponCode);
    console.log(`Checking coupon ${couponCode}: ${isUsed ? 'ALREADY USED' : 'NOT USED YET'}`);
    return isUsed;
}

/**
 * markCouponUsed - Mark a coupon as used and save to localStorage
 * @param {string} couponCode - The coupon code to mark
 * @returns {boolean} - True if successfully marked
 */
function markCouponUsed(couponCode) {
    if (!usedCoupons.includes(couponCode)) {
        usedCoupons.push(couponCode);
        saveUsedCoupons();
        console.log('Coupon marked as used and saved:', couponCode);
        console.log('All used coupons:', usedCoupons);
        return true;
    }
    console.log('Coupon already in used list:', couponCode);
    return false;
}

/**
 * clearUsedCoupons - Clear all used coupons (for testing/debugging)
 * Removes all coupon records from localStorage
 */
function clearUsedCoupons() {
    usedCoupons = [];
    localStorage.removeItem('bookmandu_used_coupons');
    showToast('All coupon records cleared', 'info');
    console.log('All used coupons cleared');
}

// Initialize - load used coupons on script load
loadUsedCoupons();

// ============================================================
// THEME
// ============================================================

/**
 * toggleTheme - Switch between light and dark mode
 * Updates data-theme attribute on html element
 * Saves preference to localStorage
 */
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  const btn = document.getElementById('theme-btn');
  if (btn) btn.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
  showToast(isDark ? '☀️ Light mode enabled' : '🌙 Dark mode enabled', 'info');
}

/**
 * Apply saved theme on page load
 * Immediately Invoked Function Expression (IIFE) that runs on script load
 * Checks localStorage for saved theme preference and applies it
 */
(function() {
  const saved = localStorage.getItem('theme');
  if (saved) {
    document.documentElement.setAttribute('data-theme', saved);
    document.addEventListener('DOMContentLoaded', () => {
      const btn = document.getElementById('theme-btn');
      if (btn) btn.textContent = saved === 'light' ? '☀️' : '🌙';
    });
  }
})();

// ============================================================
// TOAST
// ============================================================

/**
 * showToast - Display a toast notification
 * @param {string} msg - Message to display
 * @param {string} type - 'success', 'error', or 'info'
 * 
 * Creates a toast element with appropriate icon based on type
 * Auto-dismisses after 4 seconds
 */
function showToast(msg, type = 'info') {
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ'}</span><span>${msg}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  let container = document.getElementById('toasts');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toasts';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  container.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// ============================================================
// MODAL
// ============================================================

/**
 * openModal - Open a modal dialog with custom title and body
 * @param {string} title - Modal title
 * @param {string} body - Modal body HTML
 * 
 * Creates modal element if it doesn't exist
 * Sets content and opens the modal
 */
function openModal(title, body) {
  let modalOverlay = document.getElementById('modal-overlay');
  if (!modalOverlay) {
    const modalHtml = `
      <div class="modal-overlay" id="modal-overlay" onclick="closeModal(event)">
        <div class="modal">
          <div class="modal-header">
            <span class="modal-title" id="modal-title"></span>
            <button class="modal-close" onclick="closeModal()">✕</button>
          </div>
          <div id="modal-body"></div>
        </div>
      </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    modalOverlay = document.getElementById('modal-overlay');
  }
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').innerHTML = body;
  modalOverlay.classList.add('open');
}

/**
 * closeModal - Close the modal dialog
 * @param {Event} e - Click event (optional)
 * 
 * Closes modal when clicking overlay or close button
 */
function closeModal(e) {
  const modalOverlay = document.getElementById('modal-overlay');
  if (!modalOverlay) return;
  if (!e || e.target.id === 'modal-overlay' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
    modalOverlay.classList.remove('open');
  }
}

// ============================================================
// PROPERTY CARD BUILDER
// ============================================================

/**
 * buildCard - Generate HTML for a property card
 * @param {Object} p - Property object from PROPERTIES array
 * @returns {string} - HTML string for the property card
 * 
 * Includes: image placeholder, badges, wishlist button, location, title,
 * amenities, price, and rating
 */
function buildCard(p) {
  const inWishlist = wishlist.includes(p.id);
  return `
    <div class="prop-card" onclick="window.location.href='/property/${p.id}'">
      <div class="prop-img-placeholder">
        <span style="position:relative;z-index:1">${p.icon}</span>
        <div class="prop-badge-row">
          <span class="prop-type-badge">${p.type}</span>
          ${p.trending ? '<span class="prop-trending">🔥 Trending</span>' : ''}
        </div>
        <div class="prop-wishlist ${inWishlist ? 'active' : ''}" onclick="event.stopPropagation();toggleWishlist(${p.id},this)">
          ${inWishlist ? '❤️' : '🤍'}
        </div>
      </div>
      <div class="prop-body">
        <div class="prop-location">📍 ${p.region}</div>
        <div class="prop-title">${p.title}</div>
        <div class="prop-amenities">
          ${p.amenities.slice(0,3).map(a => `<span class="amenity-tag">${a}</span>`).join('')}
          ${p.amenities.length > 3 ? `<span class="amenity-tag">+${p.amenities.length-3}</span>` : ''}
        </div>
        <div class="prop-footer">
          <div class="prop-price">
            <span class="prop-price-amount">NPR ${p.price.toLocaleString()}</span>
            <span class="prop-price-night">/ night</span>
          </div>
          <div>
            <div class="prop-rating"><span class="prop-rating-star">★</span>${p.rating} <span class="prop-rating-count">(${p.reviews})</span></div>
            <div class="prop-bookings">🔥 ${p.bookings} bookings</div>
          </div>
        </div>
      </div>
    </div>`;
}

// ============================================================
// BROWSE FILTERS
// ============================================================

/**
 * getFilteredProps - Get filtered and sorted properties
 * @returns {Array} - Filtered and sorted properties array
 * 
 * Applies filters: type, price range, amenity, region (from URL param)
 * Applies sorting: price (asc/desc), rating, bookings
 */
function getFilteredProps() {
  return PROPERTIES.filter(p => {
    const typeOk = filterType === 'all' || p.type.toLowerCase().replace(/ /g,'-') === filterType;
    const priceOk = (!minPrice || p.price >= minPrice) && (!maxPrice || p.price <= maxPrice);
    const amenOk = !filterAmenity || p.amenities.map(a => a.toLowerCase()).some(a => a.includes(filterAmenity));
    const regionParam = (new URLSearchParams(window.location.search)).get('region');
    const regionOk = !regionParam || regionParam === 'all' || p.region.toLowerCase() === regionParam.toLowerCase();
    return typeOk && priceOk && amenOk && regionOk;
  }).sort((a, b) => {
    if (sortBy === 'price-asc') return a.price - b.price;
    if (sortBy === 'price-desc') return b.price - a.price;
    if (sortBy === 'rating') return b.rating - a.rating;
    return b.bookings - a.bookings;
  });
}

/**
 * applyFilter - Apply a filter and update the UI
 * @param {string} type - Filter type ('type' or 'amenity')
 * @param {string} val - Filter value
 * @param {HTMLElement} el - Element that triggered the filter
 * 
 * Updates filter state and re-renders the browse page
 */
function applyFilter(type, val, el) {
  if (type === 'type') {
    filterType = val;
    document.querySelectorAll('.filter-group .filter-pill').forEach(p => {
      if (p.getAttribute('onclick') && p.getAttribute('onclick').includes("'type'")) p.classList.remove('active');
    });
  } else if (type === 'amenity') {
    filterAmenity = filterAmenity === val ? null : val;
  }
  if (el) el.classList.toggle('active');
  if (typeof renderBrowse === 'function') renderBrowse();
}

/**
 * applyPriceFilter - Apply price range filter from input fields
 * Reads min and max price inputs and updates filter state
 */
function applyPriceFilter() {
  minPrice = +document.getElementById('price-min').value || null;
  maxPrice = +document.getElementById('price-max').value || null;
  if (typeof renderBrowse === 'function') renderBrowse();
}

/**
 * sortProperties - Sort properties by selected criteria
 * @param {string} val - Sort value ('popular', 'price-asc', 'price-desc', 'rating')
 */
function sortProperties(val) {
  sortBy = val;
  if (typeof renderBrowse === 'function') renderBrowse();
}

// ============================================================
// WISHLIST
// ============================================================

/**
 * toggleWishlist - Add or remove property from wishlist
 * @param {number} id - Property ID
 * @param {HTMLElement} btn - Wishlist button element
 * 
 * Toggles wishlist state, updates UI, and shows toast notification
 */
function toggleWishlist(id, btn) {
  const idx = wishlist.indexOf(id);
  if (idx === -1) {
    wishlist.push(id);
    if (btn) { btn.classList.add('active'); btn.textContent = '❤️'; }
    showToast('❤️ Added to wishlist!', 'success');
  } else {
    wishlist.splice(idx, 1);
    if (btn) { btn.classList.remove('active'); btn.textContent = '🤍'; }
    showToast('Removed from wishlist', 'info');
  }
}

// ============================================================
// CANCEL BOOKING MODAL
// ============================================================

/**
 * cancelBooking - Open cancellation modal for a booking
 * @param {string} ref - Booking reference number
 * 
 * Shows modal with textarea for cancellation reason
 * Submits cancellation request
 */
function cancelBooking(ref) {
  openModal('Cancel Booking', `
    <p style="color:var(--text-secondary);margin-bottom:20px">Please provide a reason for cancelling booking <strong>${ref}</strong>.</p>
    <div class="form-group" style="margin-bottom:20px">
      <label class="form-label">Reason for Cancellation</label>
      <textarea class="form-input" rows="3" placeholder="Please explain why you need to cancel..." style="resize:vertical"></textarea>
    </div>
    <div style="display:flex;gap:10px">
      <button class="btn btn-danger" style="flex:1;justify-content:center" onclick="closeModal();showToast('Cancellation requested. Host has 5 days to respond.','info')">Submit Request</button>
      <button class="btn btn-ghost" onclick="closeModal()">Keep Booking</button>
    </div>`);
}

// ============================================================
// ADD PROPERTY MODAL
// ============================================================

/**
 * showAddPropertyModal - Open modal for adding a new property
 * Hosts can submit new property listings for review
 */
function showAddPropertyModal() {
  openModal('Add New Property', `
    <div style="display:flex;flex-direction:column;gap:14px">
      <div class="form-group"><label class="form-label">Property Name</label><input class="form-input" placeholder="e.g. Mountain View Homestay"></div>
      <div class="form-group"><label class="form-label">Region</label>
        <select class="form-select"><option>Kathmandu</option><option>Pokhara</option><option>Chitwan</option><option>Lumbini</option><option>Mustang</option></select>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
        <div class="form-group"><label class="form-label">Type</label>
          <select class="form-select"><option>Homestay</option><option>Guesthouse</option><option>Private Room</option><option>Entire Property</option></select>
        </div>
        <div class="form-group"><label class="form-label">Price / Night (NPR)</label><input class="form-input" type="number" placeholder="3200"></div>
      </div>
      <div class="form-group"><label class="form-label">Max Guests</label><input class="form-input" type="number" placeholder="4" min="1" max="20"></div>
      <div class="form-group"><label class="form-label">Description</label><textarea class="form-input" rows="3" placeholder="Describe your property..." style="resize:vertical"></textarea></div>
      <button class="btn btn-primary" style="width:100%;justify-content:center" onclick="closeModal();showToast('Property submitted for admin review!','success')">Submit Listing</button>
    </div>`);
}

// ============================================================
// ENHANCED BOOKING MODAL FUNCTIONS
// ============================================================

/**
 * showEnhancedBookingModal - Display booking summary with price breakdown
 * @param {Date} selectedCheckIn - Check-in date
 * @param {Date} selectedCheckOut - Check-out date
 * @param {number} guests - Number of guests
 * @param {number} pricePerNight - Price per night
 * @param {number} nights - Number of nights
 * @param {number} subtotal - Subtotal before discount
 * @param {number} discount - Discount amount
 * @param {number} total - Total amount after discount
 * @param {string} appliedCoupon - Applied coupon code (if any)
 * @param {Object} availableCoupons - Available coupons object
 * 
 * Generates HTML for booking summary and price breakdown
 * Displays in the booking modal
 */
function showEnhancedBookingModal(selectedCheckIn, selectedCheckOut, guests, pricePerNight, nights, subtotal, discount, total, appliedCoupon, availableCoupons) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    
    const bookingSummaryHtml = `
        <div class="booking-summary-item">
            <span><i class="fas fa-building"></i> Property</span>
            <strong>🏔️ Mountain View Homestay</strong>
        </div>
        <div class="booking-summary-item">
            <span><i class="fas fa-calendar-check"></i> Check-in</span>
            <strong>${selectedCheckIn.toLocaleDateString('en-US', options)}</strong>
        </div>
        <div class="booking-summary-item">
            <span><i class="fas fa-calendar-times"></i> Check-out</span>
            <strong>${selectedCheckOut.toLocaleDateString('en-US', options)}</strong>
        </div>
        <div class="booking-summary-item">
            <span><i class="fas fa-users"></i> Guests</span>
            <strong>${guests} ${parseInt(guests) === 1 ? 'Guest' : 'Guests'}</strong>
        </div>
        <div class="booking-summary-item">
            <span><i class="fas fa-clock"></i> Stay Duration</span>
            <strong>${nights} ${nights === 1 ? 'Night' : 'Nights'}</strong>
        </div>
    `;
    
    let priceHtml = `
        <div class="row">
            <span><i class="fas fa-tag"></i> Nightly Rate</span>
            <span>NPR ${pricePerNight.toLocaleString()} × ${nights}</span>
        </div>
    `;
    
    if (appliedCoupon && availableCoupons && availableCoupons[appliedCoupon]) {
        const coupon = availableCoupons[appliedCoupon];
        priceHtml += `
            <div class="row" style="color: var(--teal);">
                <span><i class="fas fa-ticket-alt"></i> Discount (${coupon.discount}${coupon.type === 'percentage' ? '% OFF' : ' OFF'})</span>
                <span style="color: var(--teal);">-NPR ${discount.toLocaleString()}</span>
            </div>
        `;
    }
    
    priceHtml += `
        <div class="row">
            <span><i class="fas fa-wallet"></i> Subtotal</span>
            <span>NPR ${subtotal.toLocaleString()}</span>
        </div>
        <div class="row">
            <span><i class="fas fa-receipt"></i> Tax & Fees</span>
            <span>Included</span>
        </div>
        <div class="row" style="border-top: 2px solid var(--border); margin-top: 5px; padding-top: 12px;">
            <span><i class="fas fa-credit-card"></i> <strong>Total Amount</strong></span>
            <strong>NPR ${total.toLocaleString()}</strong>
        </div>
    `;
    
    const summaryDiv = document.getElementById('bookingSummary');
    const priceDiv = document.getElementById('priceBreakdown');
    if (summaryDiv) summaryDiv.innerHTML = bookingSummaryHtml;
    if (priceDiv) priceDiv.innerHTML = priceHtml;
}

/**
 * getQRCodeUrl - Generate QR code URL for payment
 * @param {number} amount - Payment amount
 * @param {string} method - Payment method (esewa, khalti, bank)
 * @returns {string} - QR code image URL
 * 
 * Uses qrserver.com API to generate QR codes
 */
function getQRCodeUrl(amount, method) {
    return 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + method.toUpperCase() + ':PAY:' + amount + ':BOOKMANDU';
}

/**
 * copyBankText - Copy bank detail text to clipboard
 * @param {string} elementId - ID of element containing text to copy
 * 
 * Uses Clipboard API to copy text
 * Shows success toast on copy
 */
function copyBankText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text);
    showToast('Copied to clipboard!', 'success');
}

// ============================================================
// COUPON APPLICATION WITH ONE-TIME USE (PERSISTENT)
// ============================================================

/**
 * applyCouponCode - Apply a coupon code to the booking
 * @param {string} couponCode - Coupon code to apply
 * @param {number} pricePerNight - Price per night
 * @param {Date} selectedCheckIn - Check-in date
 * @param {Date} selectedCheckOut - Check-out date
 * @param {number} guests - Number of guests
 * @param {Function} updateCallback - Callback function to update UI
 * @returns {Object} - Result object with success status and details
 * 
 * Features:
 * - Validates coupon exists
 * - Checks if dates are selected
 * - CRITICAL: Checks if coupon has been used (from localStorage)
 * - Calculates discount based on coupon type (percentage/fixed)
 * - Marks coupon as used immediately and saves to localStorage
 */
function applyCouponCode(couponCode, pricePerNight, selectedCheckIn, selectedCheckOut, guests, updateCallback) {
    const code = couponCode.trim().toUpperCase();
    
    if (!code) {
        return { success: false, message: 'Please enter a coupon code' };
    }
    
    // Check if coupon exists
    const coupon = window.availableCoupons[code];
    if (!coupon) {
        return { success: false, message: '❌ Invalid coupon code. Please check and try again.' };
    }
    
    // Check if dates are selected
    const nights = getNightsFromDates(selectedCheckIn, selectedCheckOut);
    if (nights === 0) {
        return { success: false, message: '📅 Please select check-in and check-out dates first' };
    }
    
    // CRITICAL: Check if coupon has already been used (from localStorage)
    if (isCouponUsed(code)) {
        return { 
            success: false, 
            message: '❌ This coupon code has already been used! Each coupon can only be used once per user/device.' 
        };
    }
    
    // Check if user already has a different coupon applied
    if (window.appliedCoupon && window.appliedCoupon !== code) {
        return { success: false, message: 'You already have a coupon applied. Remove it first to use another coupon.' };
    }
    
    window.appliedCoupon = code;
    const subtotal = nights * pricePerNight;
    let discountAmount = 0;
    
    if (coupon.type === 'percentage') {
        discountAmount = subtotal * (coupon.discount / 100);
    } else if (coupon.type === 'fixed') {
        discountAmount = Math.min(coupon.discount, subtotal);
    }
    
    window.currentDiscountValue = discountAmount;
    const total = subtotal - discountAmount;
    
    // CRITICAL: Mark this coupon as used immediately and save to localStorage
    markCouponUsed(code);
    
    return { 
        success: true, 
        message: '✅ ' + coupon.message + ' Applied Successfully!',
        discountAmount: discountAmount,
        subtotal: subtotal,
        total: total,
        couponCode: code,
        discountPercent: coupon.type === 'percentage' ? coupon.discount + '% off' : 'NPR ' + coupon.discount + ' off'
    };
}

/**
 * removeAppliedCoupon - Remove the currently applied coupon
 * @returns {Object} - Result object with success status and details
 * 
 * Note: Even after removal, the coupon remains in usedCoupons (localStorage)
 * This prevents reusing the same coupon after removal
 */
function removeAppliedCoupon() {
    if (window.appliedCoupon) {
        const removedCode = window.appliedCoupon;
        window.appliedCoupon = null;
        window.currentDiscountValue = 0;
        showToast('Coupon removed. This coupon cannot be used again as it has already been redeemed.', 'info');
        return { success: true, message: 'Coupon removed', removedCode: removedCode };
    }
    return { success: false, message: 'No coupon to remove' };
}

/**
 * getNightsFromDates - Calculate number of nights between two dates
 * @param {Date} checkIn - Check-in date
 * @param {Date} checkOut - Check-out date
 * @returns {number} - Number of nights
 */
function getNightsFromDates(checkIn, checkOut) {
    if (!checkIn || !checkOut) return 0;
    const diffTime = Math.abs(checkOut - checkIn);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * getCurrentAppliedCoupon - Get the currently applied coupon
 * @returns {string|null} - Applied coupon code or null
 */
function getCurrentAppliedCoupon() {
    return window.appliedCoupon;
}

/**
 * getCurrentDiscountValue - Get the current discount value
 * @returns {number} - Current discount amount
 */
function getCurrentDiscountValue() {
    return window.currentDiscountValue;
}

// ============================================================
// IMAGE VIEWER FUNCTIONS - COMPLETELY FIXED
// ============================================================

/**
 * bedroomImages - Array of bedroom image URLs from server
 * Used for the bedroom image viewer
 */
var bedroomImages = [
    '{{ url_for("static", filename="images/mvh2.jpg") }}',
    '{{ url_for("static", filename="images/mvh3.jpg") }}',
    '{{ url_for("static", filename="images/mvh4.jpg") }}',
    '{{ url_for("static", filename="images/mvh5.jpg") }}'
];

/**
 * galleryAllImages - Array of all gallery image URLs
 * Used for the full gallery view
 */
var galleryAllImages = [
    '{{ url_for("static", filename="images/mvh1.jpg") }}',
    '{{ url_for("static", filename="images/mvh2.jpg") }}',
    '{{ url_for("static", filename="images/mvh3.jpg") }}',
    '{{ url_for("static", filename="images/mvh4.jpg") }}',
    '{{ url_for("static", filename="images/mvh5.jpg") }}',
    '{{ url_for("static", filename="images/mvh6.jpg") }}'
];

/**
 * openImageViewer - Open single image viewer with navigation
 * @param {number} index - Index of image to display
 * 
 * Creates modal with image and Previous/Next buttons
 * Allows navigation through bedroom images
 */
function openImageViewer(index) {
    let imageModal = document.getElementById('imageViewerModal');
    if (!imageModal) {
        const modalHtml = `<div class="modal-overlay" id="imageViewerModal" onclick="closeImageViewer(event)">
            <div class="modal" style="max-width: 600px;">
                <div class="modal-header">
                    <span class="modal-title">Room View</span>
                    <button class="modal-close" onclick="closeImageViewer()">✕</button>
                </div>
                <div style="text-align: center;">
                    <img id="currentImageView" src="" alt="Room" style="width: 100%; border-radius: 12px;">
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                    <button id="prevImageBtn" style="background: var(--bg-600); border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; color: var(--text-primary); font-weight: 600;">❮ Previous</button>
                    <button id="nextImageBtn" style="background: var(--bg-600); border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; color: var(--text-primary); font-weight: 600;">Next ❯</button>
                </div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        imageModal = document.getElementById('imageViewerModal');
        
        // Add navigation functionality to Previous and Next buttons
        const prevBtn = document.getElementById('prevImageBtn');
        const nextBtn = document.getElementById('nextImageBtn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                let currentSrc = document.getElementById('currentImageView').src;
                let currentIndex = bedroomImages.findIndex(img => currentSrc.includes(img.split('/').pop()));
                if (currentIndex === -1) currentIndex = 0;
                let newIndex = currentIndex - 1;
                if (newIndex >= 0) {
                    openImageViewer(newIndex);
                } else {
                    showToast('This is the first image', 'info');
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                let currentSrc = document.getElementById('currentImageView').src;
                let currentIndex = bedroomImages.findIndex(img => currentSrc.includes(img.split('/').pop()));
                if (currentIndex === -1) currentIndex = 0;
                let newIndex = currentIndex + 1;
                if (newIndex < bedroomImages.length) {
                    openImageViewer(newIndex);
                } else {
                    showToast('This is the last image', 'info');
                }
            });
        }
    }
    const imgElement = document.getElementById('currentImageView');
    if (imgElement && bedroomImages[index]) {
        imgElement.src = bedroomImages[index];
    }
    if (imageModal) imageModal.classList.add('open');
}

/**
 * closeImageViewer - Close single image viewer
 * @param {Event} e - Click event
 * 
 * Closes when clicking overlay or close button
 */
function closeImageViewer(e) {
    const modal = document.getElementById('imageViewerModal');
    if (!modal) return;
    if (!e || e.target.id === 'imageViewerModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
        modal.classList.remove('open');
    }
}

/**
 * openAllImages - Open full gallery grid view
 * 
 * Creates modal with all images in a grid
 * Each image clickable to view full size
 * Uses closeAllImagesModal to close
 */
function openAllImages() {
    // Close any existing modal first
    closeAllImagesModal();
    
    // Create the gallery modal if it doesn't exist
    let galleryModal = document.getElementById('allImagesModal');
    
    if (!galleryModal) {
        const modalHtml = `
        <div class="modal-overlay" id="allImagesModal" onclick="closeAllImagesModal(event)">
            <div class="modal" style="max-width: 900px; width: 90%;">
                <div class="modal-header">
                    <span class="modal-title" style="font-size: 20px;">
                        <i class="fas fa-images"></i> All Property Images (${galleryAllImages.length} photos)
                    </span>
                    <button class="modal-close" onclick="closeAllImagesModal()">✕</button>
                </div>
                <div id="allImagesGrid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; max-height: 60vh; overflow-y: auto; padding: 15px;">
                    <!-- Images will be loaded here -->
                </div>
                <div class="modal-buttons" style="margin-top: 20px;">
                    <button class="btn btn-primary" onclick="closeAllImagesModal()" style="width: 100%;">Close Gallery</button>
                </div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        galleryModal = document.getElementById('allImagesModal');
    }
    
    // Populate the grid with ALL images
    const imagesGrid = document.getElementById('allImagesGrid');
    if (imagesGrid) {
        imagesGrid.innerHTML = '';
        
        // Add all gallery images (use the actual images from your property)
        galleryAllImages.forEach((imgSrc, idx) => {
            const imgDiv = document.createElement('div');
            imgDiv.style.cssText = 'cursor: pointer; border-radius: 12px; overflow: hidden; transition: all 0.2s ease; background: var(--bg-700);';
            imgDiv.className = 'gallery-grid-item';
            imgDiv.innerHTML = `
                <img src="${imgSrc}" alt="Property image ${idx + 1}" 
                     style="width: 100%; height: 160px; object-fit: cover; border-radius: 12px 12px 0 0;">
                <p style="text-align: center; margin: 8px 0; padding: 6px; font-size: 12px; color: var(--text-secondary);">
                    <i class="fas fa-image"></i> Image ${idx + 1}
                </p>
            `;
            // Click handler to close gallery and open full image viewer
            imgDiv.addEventListener('click', (function(i) {
                return function() {
                    // Close gallery and open full image viewer
                    closeAllImagesModal();
                    // For bedroom images (first 4), use bedroom viewer, otherwise use gallery viewer
                    if (i < bedroomImages.length) {
                        openImageViewer(i);
                    } else {
                        openFullImageViewer(galleryAllImages[i], i);
                    }
                };
            })(idx));
            
            // Hover effect for better UX
            imgDiv.addEventListener('mouseenter', () => {
                imgDiv.style.transform = 'translateY(-5px)';
                imgDiv.style.boxShadow = '0 8px 20px rgba(0,201,122,0.2)';
            });
            imgDiv.addEventListener('mouseleave', () => {
                imgDiv.style.transform = 'translateY(0)';
                imgDiv.style.boxShadow = 'none';
            });
            
            imagesGrid.appendChild(imgDiv);
        });
    }
    
    if (galleryModal) galleryModal.classList.add('open');
}

/**
 * openFullImageViewer - Open full-size image viewer for gallery images
 * @param {string} imageSrc - Image source URL
 * @param {number} index - Index of image in gallery
 * 
 * Similar to openImageViewer but for gallery images
 * Includes navigation through all gallery images
 */
function openFullImageViewer(imageSrc, index) {
    let fullImageModal = document.getElementById('fullImageModal');
    
    if (!fullImageModal) {
        const modalHtml = `<div class="modal-overlay" id="fullImageModal" onclick="closeFullImageViewer(event)">
            <div class="modal" style="max-width: 650px;">
                <div class="modal-header">
                    <span class="modal-title"><i class="fas fa-image"></i> Full View</span>
                    <button class="modal-close" onclick="closeFullImageViewer()">✕</button>
                </div>
                <div style="text-align: center;">
                    <img id="fullImageView" src="" alt="Full view" style="width: 100%; border-radius: 12px;">
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                    <button id="prevFullBtn" style="background: var(--bg-600); border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; color: var(--text-primary); font-weight: 600;">❮ Previous</button>
                    <button id="nextFullBtn" style="background: var(--bg-600); border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; color: var(--text-primary); font-weight: 600;">Next ❯</button>
                </div>
            </div>
        </div>`;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        fullImageModal = document.getElementById('fullImageModal');
        
        // Add navigation
        const prevBtn = document.getElementById('prevFullBtn');
        const nextBtn = document.getElementById('nextFullBtn');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', function() {
                let currentSrc = document.getElementById('fullImageView').src;
                let currentIndex = galleryAllImages.findIndex(img => currentSrc.includes(img.split('/').pop()));
                let newIndex = currentIndex - 1;
                if (newIndex >= 0) {
                    openFullImageViewer(galleryAllImages[newIndex], newIndex);
                } else {
                    showToast('This is the first image', 'info');
                }
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', function() {
                let currentSrc = document.getElementById('fullImageView').src;
                let currentIndex = galleryAllImages.findIndex(img => currentSrc.includes(img.split('/').pop()));
                let newIndex = currentIndex + 1;
                if (newIndex < galleryAllImages.length) {
                    openFullImageViewer(galleryAllImages[newIndex], newIndex);
                } else {
                    showToast('This is the last image', 'info');
                }
            });
        }
    }
    
    const imgElement = document.getElementById('fullImageView');
    if (imgElement) imgElement.src = imageSrc;
    if (fullImageModal) fullImageModal.classList.add('open');
}

/**
 * closeFullImageViewer - Close full image viewer
 * @param {Event} e - Click event
 */
function closeFullImageViewer(e) {
    const modal = document.getElementById('fullImageModal');
    if (!modal) return;
    if (!e || e.target.id === 'fullImageModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
        modal.classList.remove('open');
    }
}

/**
 * closeAllImagesModal - Close the gallery grid modal
 * @param {Event} e - Click event
 */
function closeAllImagesModal(e) {
    const modal = document.getElementById('allImagesModal');
    if (!modal) return;
    if (!e || e.target.id === 'allImagesModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close')) || (e.target && e.target.classList && e.target.classList.contains('btn-primary'))) {
        modal.classList.remove('open');
    }
}

/**
 * openFullGallery - Alias for openAllImages
 * Kept for compatibility with existing code
 */
function openFullGallery() {
    openAllImages();
}

/**
 * closeGalleryModal - Alias for closeAllImagesModal
 * Kept for compatibility with existing code
 */
function closeGalleryModal(e) {
    closeAllImagesModal(e);
}

/**
 * openFullImage - Open full image viewer for specific image
 * @param {number} index - Index of image in galleryAllImages
 */
function openFullImage(index) {
    if (galleryAllImages[index]) {
        openFullImageViewer(galleryAllImages[index], index);
    }
}

// ============================================================
// HOUSE RULES MODAL - UPDATED (REMOVED THE REFUND RULE)
// ============================================================

/**
 * showAllRules - Display all house rules in a modal
 * Shows 17 rules including: payment, cancellation, check-in/out, etc.
 * Updated to remove the refund rule as requested
 */
function showAllRules() { 
    var modal = document.getElementById('rulesModal'); 
    if (!modal) { 
        var html = '<div class="modal-overlay" id="rulesModal" onclick="closeRulesModal(event)"><div class="modal" style="max-width: 550px;"><div class="modal-header"><span class="modal-title">All House Rules (17)</span><button class="modal-close" onclick="closeRulesModal()">✕</button></div><div style="max-height: 60vh; overflow-y: auto; padding: 8px;"><div style="display: flex; flex-direction: column; gap: 16px;"><div class="rule-item"><i class="fas fa-money-bill-wave"></i> <span>A prepayment of NPR 20,000 is required.</span></div><div class="rule-item"><i class="fas fa-calendar-times"></i> <span>Cancellations within 72 hours are non-refundable.</span></div><div class="rule-item"><i class="fas fa-clock"></i> <span>Check-out: By 12:00 Noon</span></div><div class="rule-item"><i class="fas fa-clock"></i> <span>Check-in: After 3:00 PM</span></div><div class="rule-item"><i class="fas fa-utensils"></i> <span>Breakfast until 9:00 AM</span></div><div class="rule-item"><i class="fas fa-smoking-ban"></i> <span>No smoking inside</span></div><div class="rule-item"><i class="fas fa-paw"></i> <span>No pets allowed</span></div><div class="rule-item"><i class="fas fa-music"></i> <span>Quiet hours: 10 PM - 7 AM</span></div><div class="rule-item"><i class="fas fa-users"></i> <span>Max 4 guests</span></div><div class="rule-item"><i class="fas fa-glass-cheers"></i> <span>No parties or events</span></div><div class="rule-item"><i class="fas fa-camera"></i> <span>Commercial photography requires approval</span></div><div class="rule-item"><i class="fas fa-plug"></i> <span>Turn off lights/AC when leaving</span></div><div class="rule-item"><i class="fas fa-trash-alt"></i> <span>Dispose trash in bins</span></div><div class="rule-item"><i class="fas fa-door-open"></i> <span>Lock doors when leaving</span></div><div class="rule-item"><i class="fas fa-water"></i> <span>Conserve water</span></div><div class="rule-item"><i class="fas fa-child"></i> <span>Supervise children</span></div><div class="rule-item"><i class="fas fa-car"></i> <span>Park in designated areas</span></div></div></div></div></div>'; 
        document.body.insertAdjacentHTML('beforeend', html); 
        modal = document.getElementById('rulesModal'); 
    } 
    if (modal) modal.classList.add('open'); 
}

/**
 * closeRulesModal - Close the rules modal
 * @param {Event} e - Click event
 */
function closeRulesModal(e) {
    const modal = document.getElementById('rulesModal');
    if (!modal) return;
    if (!e || e.target.id === 'rulesModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
        modal.classList.remove('open');
    }
}

// ============================================================
// GLOBAL EVENT LISTENERS SETUP
// ============================================================

/**
 * setupGlobalEventListeners - Set up all global event listeners
 * 
 * Sets up:
 * - Confirm Booking button
 * - Payment method selection
 * - Proceed Payment button
 * - Confirm Payment button
 * 
 * Uses cloneNode to avoid duplicate event listeners
 * This function is called once on DOM ready
 */
function setupGlobalEventListeners() {
    // Confirm Booking Button
    const confirmBtn = document.getElementById('confirmBookingBtn');
    if (confirmBtn) {
        const newBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newBtn, confirmBtn);
        
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Confirm booking clicked');
            
            if (window.selectedCheckIn && window.selectedCheckOut) {
                const guests = document.getElementById('guests') ? document.getElementById('guests').value : 2;
                const nights = getNightsFromDates(window.selectedCheckIn, window.selectedCheckOut);
                const subtotal = nights * window.pricePerNight;
                let discount = 0;
                
                if (window.appliedCoupon && window.availableCoupons[window.appliedCoupon]) {
                    const coupon = window.availableCoupons[window.appliedCoupon];
                    if (coupon.type === 'percentage') {
                        discount = subtotal * (coupon.discount / 100);
                    } else {
                        discount = Math.min(coupon.discount, subtotal);
                    }
                }
                const total = subtotal - discount;
                
                showEnhancedBookingModal(
                    window.selectedCheckIn, 
                    window.selectedCheckOut, 
                    guests, 
                    window.pricePerNight, 
                    nights, 
                    subtotal, 
                    discount, 
                    total, 
                    window.appliedCoupon, 
                    window.availableCoupons
                );
                
                const modal = document.getElementById('bookingModal');
                if (modal) {
                    modal.classList.add('active');
                    const qrSection = document.getElementById('qrSection');
                    const paymentStatus = document.getElementById('paymentStatus');
                    const proceedBtn = document.getElementById('proceedPaymentBtn');
                    const confirmPaymentBtn = document.getElementById('confirmPaymentBtn');
                    
                    if (qrSection) qrSection.style.display = 'none';
                    if (paymentStatus) {
                        paymentStatus.className = 'payment-status';
                        paymentStatus.style.display = 'none';
                    }
                    if (proceedBtn) proceedBtn.style.display = 'flex';
                    if (confirmPaymentBtn) confirmPaymentBtn.style.display = 'none';
                    
                    const paymentMethods = document.querySelectorAll('.payment-method-enhanced');
                    paymentMethods.forEach(m => m.classList.remove('active'));
                    window.selectedPaymentMethod = null;
                } else {
                    showToast('Error opening booking modal', 'error');
                }
            } else {
                showToast('Please select check-in and check-out dates first', 'error');
            }
        });
    }
    
    // Payment Methods - Setup click handlers
    const paymentMethods = document.querySelectorAll('.payment-method-enhanced');
    paymentMethods.forEach(method => {
        const newMethod = method.cloneNode(true);
        method.parentNode.replaceChild(newMethod, method);
        
        newMethod.addEventListener('click', function() {
            document.querySelectorAll('.payment-method-enhanced').forEach(m => m.classList.remove('active'));
            this.classList.add('active');
            window.selectedPaymentMethod = this.getAttribute('data-method');
            
            const calc = { total: 0 };
            if (window.selectedCheckIn && window.selectedCheckOut) {
                const nights = getNightsFromDates(window.selectedCheckIn, window.selectedCheckOut);
                const subtotal = nights * window.pricePerNight;
                let discount = 0;
                if (window.appliedCoupon && window.availableCoupons[window.appliedCoupon]) {
                    const coupon = window.availableCoupons[window.appliedCoupon];
                    if (coupon.type === 'percentage') {
                        discount = subtotal * (coupon.discount / 100);
                    } else {
                        discount = Math.min(coupon.discount, subtotal);
                    }
                }
                calc.total = subtotal - discount;
            }
            
            const qrSection = document.getElementById('qrSection');
            const bankDetails = document.getElementById('bankDetails');
            const qrImage = document.getElementById('qrImage');
            
            if (qrSection) qrSection.style.display = 'block';
            if (window.selectedPaymentMethod === 'bank') {
                if (bankDetails) bankDetails.style.display = 'block';
                if (qrImage) qrImage.style.display = 'none';
                const paymentAmount = document.getElementById('paymentAmount');
                if (paymentAmount) paymentAmount.textContent = 'NPR ' + calc.total.toLocaleString();
            } else {
                if (bankDetails) bankDetails.style.display = 'none';
                if (qrImage) {
                    qrImage.style.display = 'block';
                    qrImage.src = getQRCodeUrl(calc.total, window.selectedPaymentMethod);
                }
            }
        });
    });
    
    // Proceed Payment Button
    const proceedBtn = document.getElementById('proceedPaymentBtn');
    if (proceedBtn) {
        const newBtn = proceedBtn.cloneNode(true);
        proceedBtn.parentNode.replaceChild(newBtn, proceedBtn);
        
        newBtn.addEventListener('click', function() {
            if (!window.selectedPaymentMethod) {
                showToast('Please select a payment method', 'error');
                return;
            }
            const statusDiv = document.getElementById('paymentStatus');
            if (statusDiv) {
                statusDiv.className = 'payment-status processing';
                statusDiv.style.display = 'block';
                statusDiv.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Processing payment...';
            }
            setTimeout(function() {
                if (statusDiv) {
                    statusDiv.className = 'payment-status success';
                    statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> Payment successful! Click "Confirm Payment" to complete.';
                }
                const proceedBtnEl = document.getElementById('proceedPaymentBtn');
                const confirmBtnEl = document.getElementById('confirmPaymentBtn');
                if (proceedBtnEl) proceedBtnEl.style.display = 'none';
                if (confirmBtnEl) confirmBtnEl.style.display = 'flex';
            }, 2000);
        });
    }
    
    // Confirm Payment Button - This is where we need to ensure coupon stays marked as used
    const confirmPaymentBtn = document.getElementById('confirmPaymentBtn');
    if (confirmPaymentBtn) {
        const newBtn = confirmPaymentBtn.cloneNode(true);
        confirmPaymentBtn.parentNode.replaceChild(newBtn, confirmPaymentBtn);
        
        newBtn.addEventListener('click', function() {
            const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
            let bookingReference = '';
            for (let i = 0; i < 10; i++) bookingReference += chars.charAt(Math.floor(Math.random() * chars.length));
            
            let total = 0;
            let usedCouponCode = null;
            if (window.selectedCheckIn && window.selectedCheckOut) {
                const nights = getNightsFromDates(window.selectedCheckIn, window.selectedCheckOut);
                const subtotal = nights * window.pricePerNight;
                let discount = 0;
                if (window.appliedCoupon && window.availableCoupons[window.appliedCoupon]) {
                    usedCouponCode = window.appliedCoupon;
                    const coupon = window.availableCoupons[window.appliedCoupon];
                    if (coupon.type === 'percentage') {
                        discount = subtotal * (coupon.discount / 100);
                    } else {
                        discount = Math.min(coupon.discount, subtotal);
                    }
                }
                total = subtotal - discount;
            }
            
            // CRITICAL: Ensure the coupon is marked as used in localStorage
            // This persists even after page refresh
            if (usedCouponCode && !isCouponUsed(usedCouponCode)) {
                markCouponUsed(usedCouponCode);
                console.log('Coupon marked as used during booking confirmation:', usedCouponCode);
            }
            
            const options = { year: 'numeric', month: 'short', day: 'numeric' };
            const bookingRefEl = document.getElementById('bookingRef');
            const successDetailsEl = document.getElementById('successDetails');
            const bookingModal = document.getElementById('bookingModal');
            const successModal = document.getElementById('successModal');
            
            if (bookingRefEl) bookingRefEl.innerHTML = 'MV-' + bookingReference;
            if (successDetailsEl) {
                successDetailsEl.innerHTML = '<p><strong>Property:</strong> Mountain View Homestay</p><p><strong>Dates:</strong> ' + 
                    window.selectedCheckIn.toLocaleDateString('en-US', options) + ' → ' + 
                    window.selectedCheckOut.toLocaleDateString('en-US', options) + 
                    '</p><p><strong>Guests:</strong> ' + (document.getElementById('guests') ? document.getElementById('guests').value : '2') + 
                    '</p><p><strong>Total Paid:</strong> NPR ' + total.toLocaleString() + '</p>';
            }
            if (bookingModal) bookingModal.classList.remove('active');
            if (successModal) successModal.classList.add('active');
            
            // Reset booking data but KEEP the used coupons in localStorage
            window.selectedCheckIn = null;
            window.selectedCheckOut = null;
            window.appliedCoupon = null;
            if (document.getElementById('couponCode')) document.getElementById('couponCode').value = '';
            const discountMsg = document.getElementById('discountMessage');
            if (discountMsg) discountMsg.style.display = 'none';
            
            if (typeof calculatePriceWithDiscount === 'function') calculatePriceWithDiscount();
            if (typeof updateBookingSummary === 'function') updateBookingSummary();
            if (typeof renderCalendar === 'function') renderCalendar();
            
            // Show confirmation that coupon is permanently used
            if (usedCouponCode) {
                showToast('✅ Booking confirmed! Your coupon has been permanently redeemed.', 'success');
            }
        });
    }
}

/**
 * closeBookingModal - Close booking modal
 */
function closeBookingModal() { 
    const modal = document.getElementById('bookingModal');
    if (modal) modal.classList.remove('active');
}

/**
 * closeSuccessModal - Close success modal
 */
function closeSuccessModal() { 
    const modal = document.getElementById('successModal');
    if (modal) modal.classList.remove('active');
}

/**
 * redirectToBrowse - Redirect to browse page
 */
function redirectToBrowse() { 
    window.location.href = "/browse"; 
}

/**
 * downloadInvoice - Download booking invoice
 * Currently shows toast - placeholder for actual implementation
 */
function downloadInvoice() { 
    showToast('Downloading invoice...', 'success'); 
}

/**
 * DOMContentLoaded - Initialize when DOM is ready
 * Sets up event listeners and logs current state
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('App.js DOM loaded, setting up event listeners');
    console.log('Currently used coupons from storage:', usedCoupons);
    setupGlobalEventListeners();
});

// ============================================================
// MAKE FUNCTIONS GLOBALLY AVAILABLE
// ============================================================

/**
 * Export all functions to window object for use in HTML
 * This makes them accessible from inline onclick handlers and other scripts
 */
window.openImageViewer = openImageViewer;
window.closeImageViewer = closeImageViewer;
window.openAllImages = openAllImages;
window.openFullGallery = openFullGallery;
window.closeGalleryModal = closeGalleryModal;
window.openFullImage = openFullImage;
window.showAllRules = showAllRules;
window.closeRulesModal = closeRulesModal;
window.applyCouponCode = applyCouponCode;
window.removeAppliedCoupon = removeAppliedCoupon;
window.getCurrentAppliedCoupon = getCurrentAppliedCoupon;
window.getCurrentDiscountValue = getCurrentDiscountValue;
window.toggleTheme = toggleTheme;
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
window.toggleWishlist = toggleWishlist;
window.cancelBooking = cancelBooking;
window.showAddPropertyModal = showAddPropertyModal;
window.showEnhancedBookingModal = showEnhancedBookingModal;
window.getQRCodeUrl = getQRCodeUrl;
window.copyBankText = copyBankText;
window.closeBookingModal = closeBookingModal;
window.closeSuccessModal = closeSuccessModal;
window.redirectToBrowse = redirectToBrowse;
window.downloadInvoice = downloadInvoice;
window.getNightsFromDates = getNightsFromDates;
window.isCouponUsed = isCouponUsed;
window.markCouponUsed = markCouponUsed;
window.clearUsedCoupons = clearUsedCoupons;
window.loadUsedCoupons = loadUsedCoupons;
window.saveUsedCoupons = saveUsedCoupons;

// Log successful initialization
console.log('Bookmandu app.js loaded successfully with PERSISTENT one-time coupon system!');
console.log('Used coupons will survive page refreshes via localStorage');