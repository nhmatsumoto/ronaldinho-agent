// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Ronaldinho Agent 🚀',
            description: 'The fenomenal autonomous engineering ecosystem.',
			social: [
                { icon: 'github', label: 'GitHub', href: 'https://github.com/nhmatsumoto/ronaldinho-agent' }
            ],
			sidebar: [
				{
					label: 'Start Here',
					items: [
						{ label: 'Introduction', slug: 'intro' },
						{ label: 'Installation', slug: 'guides/installation' },
					],
				},
				{
					label: 'Architecture',
					autogenerate: { directory: 'architecture' },
				},
                {
					label: 'Advanced',
					autogenerate: { directory: 'advanced' },
				},
			],
            customCss: [
                './src/styles/custom.css',
            ],
		}),
	],
});
