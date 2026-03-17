document.addEventListener('DOMContentLoaded', function() {
  const selectedFeatures = {};
  const selectionInfo = document.getElementById('selection-info');
  const themeToggle = document.getElementById('themeToggle');
  const featureContainer = document.getElementById('feature-container');
  const resultsList = document.getElementById('results');

  // Configure API endpoint based on environment
  const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? window.location.origin
    : 'https://your-render-backend.onrender.com'; // Replace with your Render URL

  // Load features from features.json and generate UI
  loadFeatures();

  // Theme toggle functionality
  themeToggle.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    
    if (newTheme === 'dark') {
      themeToggle.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
    } else {
      themeToggle.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
    }
    
    // Save preference to localStorage
    localStorage.setItem('theme', newTheme);
  });
  
  // Load saved theme preference
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  if (savedTheme === 'dark') {
    themeToggle.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
  }

  // Load features.json and generate the UI
  async function loadFeatures() {
    try {
      console.log('Attempting to load features.json...');
      
      // Try multiple approaches
      const urlsToTry = [
        API_BASE_URL + '/features.json',
        '/features.json',
        'features.json',
        './features.json'
      ];
      
      let response;
      let lastError;
      
      for (const url of urlsToTry) {
        try {
          console.log(`Trying URL: ${url}`);
          response = await fetch(url);
          if (response.ok) {
            console.log(`Success with URL: ${url}`);
            break;
          }
        } catch (err) {
          lastError = err;
          console.log(`Failed with URL ${url}:`, err.message);
        }
      }
      
      if (!response || !response.ok) {
        throw new Error(`Failed to fetch features.json. Tried multiple URLs. Last error: ${lastError?.message}`);
      }
      
      const features = await response.json();
      console.log('Successfully loaded features:', features);
      generateFeatureUI(features);
    } catch (error) {
      console.error('Error loading features:', error);
      featureContainer.innerHTML = `
        <div style="color: red; padding: 20px; border: 2px solid red; border-radius: 5px; background: #ffe6e6;">
          <h3>Error Loading Features</h3>
          <p><strong>Error:</strong> ${error.message}</p>
          <p><strong>Current URL:</strong> ${window.location.href}</p>
          <p><strong>Features.json should be at:</strong> ${window.location.origin}/features.json</p>
          <p>Please ensure:</p>
          <ol>
            <li>features.json exists in the same directory as app.py</li>
            <li>You've restarted the FastAPI server</li>
            <li>You can access <a href="/features.json" target="_blank">/features.json</a> directly</li>
          </ol>
        </div>
      `;
    }
  }

  function generateFeatureUI(features) {
    featureContainer.innerHTML = '';
    
    // Generate UI for each category
    for (const [category, categoryData] of Object.entries(features)) {
      const groupDiv = document.createElement('div');
      groupDiv.className = 'feature-group';
      
      // Add icon based on category
      const icon = getCategoryIcon(category);
      
      const heading = document.createElement('h3');
      heading.innerHTML = `${icon} ${formatCategoryName(category)}`;
      groupDiv.appendChild(heading);
      
      // Generate buttons for each feature
      for (const [feature, featureData] of Object.entries(categoryData)) {
        if (featureData.type === 'enum') {
          const featureName = formatFeatureName(feature);
          const subHeading = document.createElement('h4');
          subHeading.textContent = featureName;
          groupDiv.appendChild(subHeading);
          
          featureData.values.forEach(value => {
            const button = document.createElement('button');
            button.setAttribute('data-key', `${category}.${feature}`);
            button.setAttribute('data-value', value);
            button.textContent = formatValueName(value);
            groupDiv.appendChild(button);
          });
        }
      }
      
      featureContainer.appendChild(groupDiv);
    }
    
    // Add event listeners to all generated buttons
    document.querySelectorAll('#feature-container button').forEach(btn => {
      btn.addEventListener('click', handleFeatureButtonClick);
    });
  }

  function getCategoryIcon(category) {
    const icons = {
      'road': '<i class="fas fa-road"></i>',
      'google_camera': '<i class="fas fa-camera"></i>',
      'default': '<i class="fas fa-cog"></i>'
    };
    return icons[category] || icons.default;
  }

  function formatCategoryName(category) {
    // Convert snake_case to Title Case with spaces
    return category.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  function formatFeatureName(feature) {
    // Convert snake_case to Title Case with spaces
    return feature.split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  function formatValueName(value) {
    // Convert values to more readable format
    const formats = {
      'gen3': 'Gen 3',
      'gen4': 'Gen 4',
      'left': 'Left',
      'right': 'Right'
    };
    return formats[value] || value.charAt(0).toUpperCase() + value.slice(1);
  }

  function handleFeatureButtonClick(event) {
    const button = event.currentTarget;
    const key = button.dataset.key;
    const value = button.dataset.value;

    // Toggle logic (one value per feature)
    if (selectedFeatures[key] === value) {
      delete selectedFeatures[key];
      button.classList.remove("active");
    } else {
      // Deactivate other buttons in same category/feature
      document.querySelectorAll(
        `button[data-key="${key}"]`
      ).forEach(b => b.classList.remove("active"));

      selectedFeatures[key] = value;
      button.classList.add("active");
    }

    updateSelectionInfo();
    sendRequest();
  }

  function updateSelectionInfo() {
    const count = Object.keys(selectedFeatures).length;
    if (count === 0) {
      selectionInfo.innerHTML = '<i class="fas fa-info-circle"></i> No features selected yet.';
    } else {
      const features = Object.entries(selectedFeatures)
        .map(([k, v]) => {
          const [category, feature] = k.split('.');
          return `<strong>${formatCategoryName(category)} - ${formatFeatureName(feature)}</strong>: ${formatValueName(v).replace(/<[^>]*>/g, '')}`;
        })
        .join(', ');
      selectionInfo.innerHTML = `<i class="fas fa-check-circle"></i> Selected: ${features}`;
    }
  }

  // Function to get color based on score (0-1)
  function getScoreColor(score) {
    // Red (0) -> Yellow (0.5) -> Green (1)
    const hue = score * 120; // 0 = red, 120 = green
    return `hsl(${hue}, 70%, 50%)`;
  }

  async function sendRequest() {
    if (Object.keys(selectedFeatures).length === 0) {
      renderResults([]);
      return;
    }

    try {
      const res = await fetch(API_BASE_URL + "/narrow", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          selected_features: selectedFeatures
        })
      });

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();
      renderResults(data);
    } catch (error) {
      console.error('Error:', error);
      resultsList.innerHTML = '<li class="no-results" style="color: #e74c3c;">Error connecting to server. Make sure Python server is running (uvicorn app:app --reload)</li>';
    }
  }

  function renderResults(results) {
    resultsList.innerHTML = "";

    if (results.length === 0) {
      const li = document.createElement("li");
      li.className = "no-results";
      li.textContent = "No countries match all selected features.";
      resultsList.appendChild(li);
      return;
    }

    results.forEach(r => {
      const li = document.createElement("li");
      li.textContent = r.name;
      
      // Set background color based on score
      const color = getScoreColor(r.score);
      li.style.backgroundColor = color;
      
      // Add tooltip with details
      const tooltip = document.createElement("span");
      tooltip.className = "tooltip";
      tooltip.innerHTML = `${r.matched}/${r.total} features matched<br>${(r.score * 100).toFixed(0)}% similarity`;
      li.appendChild(tooltip);
      
      resultsList.appendChild(li);
    });
  }

  // Initialize
  updateSelectionInfo();
});