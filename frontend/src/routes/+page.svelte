<script
  import { onMount } from 'svelte';
  import { apiClient } from '$lib/api';
  import { formatCurrency } from '$lib/types';
  import { Package } from '$lib/types';

  let packages=
  let loading = true;
  let error = '';

  onMount(async () => {
    try {
      packages = await apiClient.getPackages();
    } catch (err) {
      error = errload pack||ges';
    } finally {
      loading = false;
    }
  });

  function handleBuyPackage(packageTier
    // Redirect to signup/login with package selection
    window.location.href = `/signup?package=${packageTier}`;
  }
</script>

<T