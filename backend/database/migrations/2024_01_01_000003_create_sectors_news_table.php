<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('sectors', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('name_en')->nullable();
            $table->string('code')->unique()->nullable();
            $table->text('description')->nullable();
            $table->timestamps();
        });

        Schema::create('news', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->string('title_en')->nullable();
            $table->text('content');
            $table->text('content_en')->nullable();
            $table->string('category')->default('market'); // market, companies, economy, international
            $table->string('source')->nullable();
            $table->string('url')->nullable();
            $table->string('image_url')->nullable();
            $table->timestamp('published_at')->nullable();
            $table->boolean('is_published')->default(true);
            $table->timestamps();
        });

        Schema::create('stock_news', function (Blueprint $table) {
            $table->id();
            $table->foreignId('news_id')->constrained()->cascadeOnDelete();
            $table->string('symbol');
            $table->index(['news_id', 'symbol']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('stock_news');
        Schema::dropIfExists('news');
        Schema::dropIfExists('sectors');
    }
};
