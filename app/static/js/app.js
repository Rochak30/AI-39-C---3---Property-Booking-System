/* ============================================================
   BOOKMANDU — SHARED APP.JS
   All shared data, state, utilities, and UI helpers.
   Include this in every page via base.html.
   ============================================================ */

// ============================================================
// DATA
// ============================================================
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

const BOOKINGS_DATA = [
  { ref:"BM-A7K2M9PQ", prop:"Mountain View Homestay", icon:"🏔", dates:"May 20–23, 2026", guests:2, status:"confirmed", amount:"NPR 9,600" },
  { ref:"BM-C3L8N5RX", prop:"Lakeside Comfort Inn", icon:"🏞", dates:"Jun 5–8, 2026", guests:2, status:"pending", amount:"NPR 5,400" },
  { ref:"BM-K1P4Q7YZ", prop:"Thamel Heritage House", icon:"🕌", dates:"Mar 10–13, 2026", guests:3, status:"cancelled", amount:"NPR 8,400" },
];

// ============================================================
// STATE
// ============================================================
let wishlist = [1, 3, 6];
let filterType = 'all';
let filterAmenity = null;
let minPrice = null, maxPrice = null;
let sortBy = 'popular';

// ============================================================
// THEME
// ============================================================
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  const btn = document.getElementById('theme-btn');
  if (btn) btn.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
  showToast(isDark ? '☀️ Light mode enabled' : '🌙 Dark mode enabled', 'info');
}

// Apply saved theme on load
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
function showToast(msg, type = 'info') {
  const icons = { success: '✓', error: '✕', info: 'ℹ' };
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ'}</span><span>${msg}</span><span class="toast-close" onclick="this.parentElement.remove()">✕</span>`;
  const container = document.getElementById('toasts');
  if (container) container.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

// ============================================================
// MODAL
// ============================================================
function openModal(title, body) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').innerHTML = body;
  document.getElementById('modal-overlay').classList.add('open');
}
function closeModal(e) {
  if (!e || e.target.id === 'modal-overlay' || e.target.classList.contains('modal-close')) {
    document.getElementById('modal-overlay').classList.remove('open');
  }
}

// ============================================================
// PROPERTY CARD BUILDER (used on home + browse)
// ============================================================
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

function applyPriceFilter() {
  minPrice = +document.getElementById('price-min').value || null;
  maxPrice = +document.getElementById('price-max').value || null;
  if (typeof renderBrowse === 'function') renderBrowse();
}

function sortProperties(val) {
  sortBy = val;
  if (typeof renderBrowse === 'function') renderBrowse();
}

// ============================================================
// WISHLIST
// ============================================================
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
// CANCEL BOOKING MODAL (guest dashboard)
// ============================================================
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
// ADD PROPERTY MODAL (host dashboard)
// ============================================================
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
// IMAGE VIEWER FUNCTIONS - FULLY WORKING
// ============================================================

// Array of bedroom images
var bedroomImages = [
    'https://images.unsplash.com/photo-1566665797739-1674de7a421a?w=800',
    'https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?w=800',
    'https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=800',
    'https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?w=800'
];

// Array of all gallery images
var galleryAllImages = [
    'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
    'https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800',
    'https://images.unsplash.com/photo-1468413253725-0d518109b803?w=800',
    'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800',
    'https://images.unsplash.com/photo-1580829732192-817f0fd9d7cf?w=800',
    'https://images.unsplash.com/photo-1558798539-e7d702ca26a9?w=800'
];

function openImageViewer(index) {
    var imageModal = document.getElementById('imageViewerModal');
    if (!imageModal) {
        var modalHtml = '<div class="modal-overlay" id="imageViewerModal" onclick="closeImageViewer(event)">' +
            '<div class="modal" style="max-width: 600px;">' +
            '<div class="modal-header">' +
            '<span class="modal-title">Bedroom View</span>' +
            '<button class="modal-close" onclick="closeImageViewer()">✕</button>' +
            '</div>' +
            '<div id="imageViewerBody" style="text-align: center;">' +
            '<img id="currentImageView" src="" alt="Bedroom" style="width: 100%; border-radius: 12px;">' +
            '</div>' +
            '</div>' +
            '</div>';
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        imageModal = document.getElementById('imageViewerModal');
    }
    var imgElement = document.getElementById('currentImageView');
    if (imgElement && bedroomImages[index]) {
        imgElement.src = bedroomImages[index];
    }
    if (imageModal) imageModal.classList.add('open');
}

function closeImageViewer(e) {
    var modal = document.getElementById('imageViewerModal');
    if (!e || e.target.id === 'imageViewerModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
        if (modal) modal.classList.remove('open');
    }
}

function openAllImages() {
    if (bedroomImages.length > 0) {
        openImageViewer(0);
    } else {
        showToast('No images available', 'error');
    }
}

function openFullGallery() {
    var galleryModal = document.getElementById('galleryModal');
    if (!galleryModal) {
        var galleryHtml = '<div class="modal-overlay" id="galleryModal" onclick="closeGalleryModal(event)">' +
            '<div class="modal" style="max-width: 700px;">' +
            '<div class="modal-header">' +
            '<span class="modal-title">Property Gallery</span>' +
            '<button class="modal-close" onclick="closeGalleryModal()">✕</button>' +
            '</div>' +
            '<div id="galleryBody" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; max-height: 60vh; overflow-y: auto; padding: 8px;">' +
            '</div>' +
            '</div>' +
            '</div>';
        document.body.insertAdjacentHTML('beforeend', galleryHtml);
        galleryModal = document.getElementById('galleryModal');
    }
    var galleryBody = document.getElementById('galleryBody');
    if (galleryBody) {
        galleryBody.innerHTML = '';
        for (var i = 0; i < galleryAllImages.length; i++) {
            galleryBody.innerHTML += '<img src="' + galleryAllImages[i] + '" alt="Gallery image" style="width: 100%; border-radius: 12px; cursor: pointer; margin-bottom: 8px;" onclick="openFullImage(' + i + ')">';
        }
    }
    if (galleryModal) galleryModal.classList.add('open');
}

function closeGalleryModal(e) {
    var modal = document.getElementById('galleryModal');
    if (!e || e.target.id === 'galleryModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
        if (modal) modal.classList.remove('open');
    }
}

function openFullImage(index) {
    closeGalleryModal();
    if (galleryAllImages[index]) {
        var tempModal = document.getElementById('imageViewerModal');
        if (!tempModal) {
            var modalHtml = '<div class="modal-overlay" id="imageViewerModal" onclick="closeImageViewer(event)">' +
                '<div class="modal" style="max-width: 600px;">' +
                '<div class="modal-header">' +
                '<span class="modal-title">Photo View</span>' +
                '<button class="modal-close" onclick="closeImageViewer()">✕</button>' +
                '</div>' +
                '<div id="imageViewerBody" style="text-align: center;">' +
                '<img id="currentImageView" src="" alt="Photo" style="width: 100%; border-radius: 12px;">' +
                '</div>' +
                '</div>' +
                '</div>';
            document.body.insertAdjacentHTML('beforeend', modalHtml);
            tempModal = document.getElementById('imageViewerModal');
        }
        var imgElement = document.getElementById('currentImageView');
        if (imgElement) imgElement.src = galleryAllImages[index];
        if (tempModal) tempModal.classList.add('open');
    }
}

// ============================================================
// HOUSE RULES MODAL - FULLY WORKING
// ============================================================

function showAllRules() {
    var rulesModal = document.getElementById('rulesModal');
    if (!rulesModal) {
        var modalHtml = '<div class="modal-overlay" id="rulesModal" onclick="closeRulesModal(event)">' +
            '<div class="modal" style="max-width: 550px;">' +
            '<div class="modal-header">' +
            '<span class="modal-title">All House Rules (18)</span>' +
            '<button class="modal-close" onclick="closeRulesModal()">✕</button>' +
            '</div>' +
            '<div id="rulesBody" style="max-height: 60vh; overflow-y: auto; padding: 8px;">' +
            '<div style="display: flex; flex-direction: column; gap: 16px;">' +
            '<div class="rule-item"><i class="fas fa-money-bill-wave"></i> <span>A prepayment of NPR 20,000 is required to confirm your booking.</span></div>' +
            '<div class="rule-item"><i class="fas fa-calendar-times"></i> <span>Cancellations within 72 hours of arrival are non-refundable.</span></div>' +
            '<div class="rule-item"><i class="fas fa-clock"></i> <span>Check-out: By 12:00 Noon</span></div>' +
            '<div class="rule-item"><i class="fas fa-refund"></i> <span>Full prepayment refunds are available for cancellations made at least 72 hours before check-in.</span></div>' +
            '<div class="rule-item"><i class="fas fa-clock"></i> <span>Check-in: After 3:00 PM</span></div>' +
            '<div class="rule-item"><i class="fas fa-utensils"></i> <span>Breakfast is served until 9:00 AM; service concludes at 9:30 AM.</span></div>' +
            '<div class="rule-item"><i class="fas fa-smoking-ban"></i> <span>No smoking inside the property</span></div>' +
            '<div class="rule-item"><i class="fas fa-paw"></i> <span>Pets are not allowed</span></div>' +
            '<div class="rule-item"><i class="fas fa-music"></i> <span>Quiet hours: 10 PM - 7 AM</span></div>' +
            '<div class="rule-item"><i class="fas fa-users"></i> <span>Maximum 4 guests per booking</span></div>' +
            '<div class="rule-item"><i class="fas fa-glass-cheers"></i> <span>No parties or events</span></div>' +
            '<div class="rule-item"><i class="fas fa-camera"></i> <span>Commercial photography requires prior approval</span></div>' +
            '<div class="rule-item"><i class="fas fa-plug"></i> <span>Please turn off lights and AC when leaving</span></div>' +
            '<div class="rule-item"><i class="fas fa-trash-alt"></i> <span>Dispose of trash in designated bins</span></div>' +
            '<div class="rule-item"><i class="fas fa-door-open"></i> <span>Always lock doors when leaving</span></div>' +
            '<div class="rule-item"><i class="fas fa-water"></i> <span>Conserve water - report any leaks</span></div>' +
            '<div class="rule-item"><i class="fas fa-child"></i> <span>Children must be supervised at all times</span></div>' +
            '<div class="rule-item"><i class="fas fa-car"></i> <span>Park only in designated areas</span></div>' +
            '</div>' +
            '</div>' +
            '</div>' +
            '</div>';
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        rulesModal = document.getElementById('rulesModal');
    }
    if (rulesModal) rulesModal.classList.add('open');
}

function closeRulesModal(e) {
    var modal = document.getElementById('rulesModal');
    if (!e || e.target.id === 'rulesModal' || (e.target && e.target.classList && e.target.classList.contains('modal-close'))) {
        if (modal) modal.classList.remove('open');
    }
}

// Make functions globally available for onclick handlers
window.openImageViewer = openImageViewer;
window.closeImageViewer = closeImageViewer;
window.openAllImages = openAllImages;
window.openFullGallery = openFullGallery;
window.closeGalleryModal = closeGalleryModal;
window.openFullImage = openFullImage;
window.showAllRules = showAllRules;
window.closeRulesModal = closeRulesModal;