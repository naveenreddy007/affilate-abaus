<script lang="ts">
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api';
  import { formatCurrency } from '$lib/types';
  import type { Package } from '$lib/types';

  let packages: Package[] = [];
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      packages = await apiClient.getPackages();
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to load packages';
    } finally {
      loading = false;
    }
  });

  function handleBuyPackage(packageTier: string) {
    // Redirect to signup/login with package selection
    window.location.href = `/signup?package=${packageTier}`;
  }
</script>

<svelte:head>
  <title>Affiliate Learning Platform - Learn & Earn</title>
  <meta name="description" content="Join our affiliate learning platform and start earning commissions while learning valuable skills." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
    <div class="text-center">
      <h1 class="text-4xl md:text-6xl font-bold mb-6">
        Learn Skills, <span class="text-yellow-300">Earn Money</span>
      </h1>
      <p class="text-xl md:text-2xl mb-8 text-primary-100 max-w-3xl mx-auto">
        Join our affiliate learning platform where you can access premium courses and earn commissions by referring others.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <a href="/courses" class="btn-secondary text-lg px-8 py-3">
          Browse Free Courses
        </a>
        <a href="/signup" class="btn bg-yellow-400 text-gray-900 hover:bg-yellow-300 text-lg px-8 py-3">
          Get Started Free
        </a>
      </div>
    </div>
  </div>
</section>

<!-- Features Section -->
<section class="py-20 bg-white">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
        Why Choose Our Platform?
      </h2>
      <p class="text-xl text-gray-600 max-w-2xl mx-auto">
        We combine high-quality education with a rewarding affiliate system.
      </p>
    </div>

    <div class="grid md:grid-cols-3 gap-8">
      <div class="text-center">
        <div class="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">Quality Courses</h3>
        <p class="text-gray-600">Access premium video courses designed by industry experts.</p>
      </div>

      <div class="text-center">
        <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">Earn Commissions</h3>
        <p class="text-gray-600">Get rewarded for referring friends and building your network.</p>
      </div>

      <div class="text-center">
        <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-semibold mb-2">Community Support</h3>
        <p class="text-gray-600">Join a community of learners and entrepreneurs.</p>
      </div>
    </div>
  </div>
</section>

<!-- Packages Section -->
<section class="py-20 bg-gray-50">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-16">
      <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
        Choose Your Package
      </h2>
      <p class="text-xl text-gray-600 max-w-2xl mx-auto">
        Unlock affiliate earning potential with our premium packages.
      </p>
    </div>

    {#if loading}
      <div class="text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-gray-600">Loading packages...</p>
      </div>
    {:else if error}
      <div class="text-center text-red-600">
        <p>Error: {error}</p>
      </div>
    {:else}
      <div class="grid md:grid-cols-3 gap-8">
        {#each packages as pkg}
          <div class="card relative {pkg.tier === 'gold' ? 'ring-2 ring-primary-500' : ''}">
            {#if pkg.tier === 'gold'}
              <div class="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span class="bg-primary-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
            {/if}
            
            <div class="text-center">
              <h3 class="text-2xl font-bold text-gray-900 mb-2">{pkg.name}</h3>
              <div class="mb-4">
                <span class="text-4xl font-bold text-gray-900">{formatCurrency(pkg.final_price)}</span>
                <span class="text-gray-500 text-sm block">Including 18% GST</span>
              </div>
              
              <ul class="text-left space-y-2 mb-8">
                {#each pkg.features as feature}
                  <li class="flex items-center">
                    <svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    {feature}
                  </li>
                {/each}
              </ul>
              
              <button 
                class="btn-primary w-full"
                on:click={() => handleBuyPackage(pkg.tier)}
              >
                Get Started
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </div>
</section>

<!-- CTA Section -->
<section class="py-20 bg-primary-600 text-white">
  <div class="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
    <h2 class="text-3xl md:text-4xl font-bold mb-4">
      Ready to Start Learning and Earning?
    </h2>
    <p class="text-xl mb-8 text-primary-100">
      Join thousands of learners who are already building their skills and income.
    </p>
    <a href="/signup" class="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-3">
      Sign Up Free Today
    </a>
  </div>
</section>